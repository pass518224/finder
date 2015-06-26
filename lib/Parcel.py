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

logger = logging.getLogger(__name__)
BYTE = 4

def hook(func):
    def hookFunction(self, *args, **kargs):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 1)
        code = calframe[1][4][0].replace(' ', "").replace("\n", "")
        print "module: {}:{}".format(calframe[1][1], calframe[1][2])
        _result = func(self, *args, **kargs)
        print "\t{}    #{}".format(code, _result)
        return _result
    return hookFunction

class Parcel(object):
    """Parcel object to contain data"""
    def __init__(self, raw):
        super(Parcel, self).__init__()
        self.data = base64.b64decode(raw)
        self.offset = 0

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
            return null

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
        
    @hook
    def readString(self):
        result = self.readString16()
        if  len(result) == 0:
            result = String("")
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
        if  length == 0:
            return String("")
        length += 1
        offset = self.offset
        self.offset += length*2
        self.offset = (self.offset + 3) &~ 3
        if  self.offset > len(self.data):
            raise IllegalParcel("Offset out of bound.", "from offset: 0x{:x}, get length: {}, become: {}".format(offset, length, self.offset))
        return String(self.data[offset: self.offset].decode("utf16").encode("utf8").strip("\x00"))

    @hook
    def readParcelable(self, loader):
        raise NoneImplementFunction("readParcelable")
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
        raise NoneImplementFunction(inspect.stack()[1][3])
        """TODO """
        return None

    @hook
    def createTypedArray(self, creator):
        raise NoneImplementFunction(inspect.stack()[1][3])
        """TODO """
        return None

    """
    reply functions
    #! ideally, not used
    """

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
