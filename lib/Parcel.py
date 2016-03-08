import logging
import binascii
import string
import struct
import inspect
import base64

from JavaUtils.String import String
from JavaUtils.IBinder import IBinder
from PersistableBundle import PersistableBundle
from Bundle import Bundle

import tools.Config as Config

logger = logging.getLogger(__name__)
BYTE = 4

def hook(func):
    def hookFunction(self, *args, **kargs):
        if  not Config.DEBUG:
            _result = func(self, *args, **kargs)
            return _result
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 1)
        code = calframe[1][4][0].replace(' ', "").replace("\n", "")
        print "module: {}:{}".format(calframe[1][1], calframe[1][2])
        _result = func(self, *args, **kargs)
        print "\t{}    #{}".format(code, _result)
        return _result
    return hookFunction

VAL_NULL = -1;
VAL_STRING = 0;
VAL_INTEGER = 1;
VAL_MAP = 2;
VAL_BUNDLE = 3;
VAL_PARCELABLE = 4;
VAL_SHORT = 5;
VAL_LONG = 6;
VAL_FLOAT = 7;
VAL_DOUBLE = 8;
VAL_BOOLEAN = 9;
VAL_CHARSEQUENCE = 10;
VAL_LIST  = 11;
VAL_SPARSEARRAY = 12;
VAL_BYTEARRAY = 13;
VAL_STRINGARRAY = 14;
VAL_IBINDER = 15;
VAL_PARCELABLEARRAY = 16;
VAL_OBJECTARRAY = 17;
VAL_INTARRAY = 18;
VAL_LONGARRAY = 19;
VAL_BYTE = 20;
VAL_SERIALIZABLE = 21;
VAL_SPARSEBOOLEANARRAY = 22;
VAL_BOOLEANARRAY = 23;
VAL_CHARSEQUENCEARRAY = 24;
VAL_PERSISTABLEBUNDLE = 25;
VAL_SIZE = 26;
VAL_SIZEF = 27;

class Parcel(object):
    """Parcel object to contain data"""
    def __init__(self, raw):
        self.data = base64.b64decode(raw)
        self.offset = 0

    def setData(self, data):
        self.data = data

    @hook
    def enforceInterface(self, descriptor):
        policy = self.readInt()
        return self.readString()

    @hook
    def readStrongBinder(self):
        return IBinder(self.readObject(False))

    @hook
    def readObject(self, nullMetaData):
        self.offset += BYTE *4
        """ TODO """
        return "<<Strong binder>>"

    @hook
    def readPersistableBundle(self, loader=None):
        length = self.readInt()
        if  length < 0:
            return None

        bundle = PersistableBundle(self, length)
        if  loader != None:
            bundle.setClassLoader(loader)

        return bundle


    @hook
    def readByte(self):
        return self.readInt() & 0xff

    @hook
    def readLong(self):
        return self.readInt64()

    @hook
    def readInt(self):
        return self.readInt32()

    def readInt32(self):
        offset = self.offset
        self.offset += 4
        try:
            return struct.unpack("<i", self.data[offset: self.offset])[0]
        except struct.error as e:
            return 0
            raise IllegalParcel(e.args[0], "data[0x{:x}:0x{:x}] : {}".format(offset, self.offset, self.data[offset:self.offset].encode("hex")))

    def readInt64(self):
        offset = self.offset
        self.offset += 8
        try:
            return struct.unpack("<i", self.data[offset: self.offset])[0]
        except struct.error as e:
            return 0
            raise IllegalParcel(e.args[0], "data[0x{:x}:0x{:x}] : {}".format(offset, self.offset, self.data[offset:self.offset].encode("hex")))

    @hook
    def readFloat(self):
        offset = self.offset
        self.offset += 4
        try:
            return struct.unpack("<f", self.data[offset: self.offset])[0]
        except struct.error as e:
            return 0
            raise IllegalParcel(e.args[0], "data[0x{:x}:0x{:x}] : {}".format(offset, self.offset, self.data[offset:self.offset].encode("hex")))

    @hook
    def readBundle(self, loader=None):
        length = self.readInt()
        if  length < 0:
            return None
        bundle = Bundle(self, length)
        if  loader != None:
            bundle.setClassLoader(loader)
        return bundle

    def readArrayMapInternal(self, map, N, loader):
        while N > 0:
            key = self.readString()
            val = self.readValue(loader)
            map[key] = val
            N -= 1

    def readValue(self, loader):
        type = self.readInt()
        
        if  type==VAL_NULL:
            return None
        elif type == VAL_STRING:
            return self.readString()
        elif type == VAL_INTEGER:
            return self.readInt()
        elif type == VAL_MAP:
            return self.readHashMap(loader)
        elif type == VAL_PARCELABLE:
            return self.readParcelable(loader)
        elif type == VAL_SHORT:
            return self.readInt()
        elif type == VAL_LONG:
            return self.readLong()
        elif type == VAL_FLOAT:
            return self.readFloat()
        elif type == VAL_DOUBLE:
            return self.readDouble()
        elif type == VAL_BOOLEAN:
            return self.readint() == 1
        elif type == VAL_LIST:
            return self.readArrayList(loader)
        elif type == VAL_BOOLEANARRAY:
            return self.createBooleanArray()
        elif type == VAL_BYTEARRAY:
            return self.createByteArray()
        elif type == VAL_STRINGARRAY:
            return self.readStringArray()
        elif type == VAL_IBINDER:
            return self.readStrongBinder()
        elif type == VAL_OBJECTARRAY:
            return self.readArray()
        elif type == VAL_INTARRAY:
            return self.createIntArray()
        elif type == VAL_LONGARRAY:
            return self.createLongArray()
        elif type == VAL_BYTE:
            return self.readByte()
        
    @hook
    def readString(self):
        result = self.readString16()
        return result

    @hook
    def readStringArray(self):
        length = self.readInt()
        if  0 <= length:
            return [self.readString() for i in range(length)]
        else:
            return None

    @hook
    def readStringList(self, arrayList):
        M = arrayList.size();
        N = self.readInt()
        i = 0
        while( i < M and i < N):
            arrayList.set(i, self.readString())
            i += 1

        while i < N:
            arrayList.add(self.readString())
            i += 1

        while i < M:
            arrayList.remove(N)
            i += 1


    def readString16(self):
        length = self.readInt32()
        if  length < 0:
            return None
        length += 1
        offset = self.offset
        self.offset += length*2
        self.offset = (self.offset + 3) &~ 3
        if  self.offset > len(self.data):
            raise IllegalParcel("Offset out of bound.", "from offset: 0x{:x}, get length: {}, become: {}".format(offset, length, self.offset))
        return String(self.data[offset: self.offset].decode("utf16").encode("utf8").strip("\x00"))

    @hook
    def readParcelable(self, loader):
        raise NoneImplementFunction("readParcelable loader:{}".format(loader))
        creator = self.readParcelableCreator(loader)
        if  creator == None:
            return None

    @hook
    def readParcelableCreator(self, loader):
        name = self.readString()
        if  name == None:
            return None


    def getDescriptor(self):
        self.offset = 4
        descriptor = self.readString16()
        self.offset = 0
        return descriptor

    def getEncodedRaw(self):
        return base64.b64encode(self.data)

    @hook
    def createIntArray(self):
        length = self.readInt()
        if  0 <= length and length <= (( len(self.data) - self.offset) / 4):
            return [self.readInt() for i in range(length)]
        else:
            return None

    @hook
    def createStringArray(self):
        length = self.readInt()
        if  0 <= length:
            return [self.readString() for i in range(length)]
        else:
            return None

    @hook
    def createTypedArrayList(self, creator):
        """ temporary fix """
        if  type(creator) == str:
            if creator == "ResultInfo":
                from android.app.ResultInfo import *
                creator = ResultInfo.CREATOR
            elif creator == "ProviderInfo":
                from android.content.pm.ProviderInfo import *
                creator = ProviderInfo.CREATOR
            elif creator == "ContentProviderHolder":
                from android.app.IActivityManager import *
                creator = ContentProviderHolder.CREATOR
            elif creator == "ReferrerIntent":
                from com.android.internal.content.ReferrerIntent import *
                creator = ReferrerIntent.CREATOR
            else:
                print creator
        n = self.readInt()
        if  n < 0:
            return None

        I = list()
        while n > 0:
            if  self.readInt() != 0:
                I.append(creator.createFromParcel(self))
            else:
                I.append(null)
            n -= 1
        return I

    @hook
    def createTypedArray(self, creator):
        """ temporary fix """
        if  type(creator) == str:
            if creator == "Intent":
                from android.content.Intent import *
                creator = Intent.CREATOR
            elif creator == "android.view.inputmethod.InputMethodSubtype":
                from android.view.inputmethod.InputMethodSubtype import *
                creator = InputMethodSubtype.CREATOR
            elif creator == "android.content.ComponentName":
                from android.content.ComponentName import *
                creator = ComponentName.CREATOR
            else:
                print creator
        n = self.readInt()
        if  n < 0:
            return None

        I = [None]*n
        for i in range(n):
            if  self.readInt() != 0:
                I[i] = creator.createFromParcel(self)
        return I

    """
    reply functions
    #! ideally, not used
    """

    def hasFileDescriptors(self):
        """docstring for ha"""
        pass

    def writeNoException(self):
        return

    def __str__(self):
        return self.hexdump()

    def __repr__(self):
        return "'<Parcel Object: " + ''.join([i if 31 < ord(i) < 127 else '' for i in self.data]) + ">'"

    def hexdump(self, length=32):
        src = self.data
        FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
        lines = []
        lines.append("    " + " ".join(["%02x" % x for x in range(32)]) + "\n")
        for c in xrange(0, len(src), length):
            chars = src[c:c+length]
            hex = ' '.join(["%02x" % ord(x) for x in chars])
            printable = ''.join(["%s" % ((ord(x) <= 127 and FILTER[ord(x)]) or '.') for x in chars])
            lines.append("%04x  %-*s  %s\n" % (c, length*3, hex, printable))
        return ''.join(lines)
        
class IllegalParcel(Exception):
    pass

class NoneImplementFunction(Exception):
    pass

if __name__ == '__main__':
    #hex = "870b00002000000061006e00640072006f00690064002e006e00650074002e0049004e006500740077006f0072006b0053007400610074007300530065007200760069006300650000000000"
    hex = "2000000061007200640072006f00690064002e006e00650074002e0049004e006500740077006f0072006b0053007400610074007300530065007200760069006300650000000000"
    p = Parcel(hex)
    print p.hexdump()
    id = p.readString16()
    print id
