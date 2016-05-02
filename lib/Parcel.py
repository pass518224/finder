
import logging
import pydoc
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
import __builtin__
import re

logger = logging.getLogger(__name__)
BYTE = 4

def hook(func):
    def hookFunction(self, *args, **kargs):
        if Config.DEBUG or Config.JSONOUTPUT:
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 1)
            code = calframe[1][4][0].replace(' ', "").replace("\n", "")

        if Config.DEBUG:
            print "module: {}:{}".format(calframe[1][1], calframe[1][2])

        _result = func(self, *args, **kargs)

        if Config.JSONOUTPUT or Config.DEBUG:
            result_str = str(_result)

        if Config.DEBUG:
            print "\t{}    #{}".format(code, result_str)

        if Config.JSONOUTPUT:
            json(calframe, result_str)

        return _result

    def json(calframe, result_str):
        code = calframe[1][4][0].replace(' ', "").replace("\n", "")
        # caller is not a if statement and caller is not "enforceInterface"
        if not re.match('(\W|^)if\W', code) and calframe[1][3] != "enforceInterface":
            # a list of keyword from call frame
            # "_" mains return statement
            keylist = [] if calframe[1][4][0].find("return") < 0 else [("_", None)]
            # a wrapper of keylist because of the closure
            keylistlist = [keylist]

            # traverse call frame
            for f in calframe[1:]:
                # skip hookFunction and creatorResolver
                if f[3] == "hookFunction" or f[3] == "creatorResolver":
                    continue
                stmt = f[4][0].replace(' ', '')
                # search the pattern in stmt, and add result to keylist
                def searchAndAppend(expression, t = None):
                    res = re.search(expression, stmt)
                    if res:
                        keylistlist[0] = [(res.group(1), t)] + keylistlist[0]
                    return res
                # search all assign statement (exclude == and !=)
                if searchAndAppend('(\w+)=[^=]'): pass
                # ex. ".setAction()"
                elif searchAndAppend('\.set(\w+)'): pass
                # ex. "readStringList()"
                elif searchAndAppend('read(\w*List)'): pass
                # ex. "arrayList.add(...)""
                elif searchAndAppend('(\w+)\.add', 'list'): pass
                # ex "readArrayMapInternel()"
                elif searchAndAppend('read(\w*ArrayMap)', 'list'): pass
                # stop condition
                if f[3] == "onTransact":
                    break

            keylist = keylistlist[0]
            # restore result
            if keylist != []:
                # recursive function
                # based on keylist, find a object to restore result
                # return None if the result is already in subobject
                def search(subobject, keylist):
                    key = keylist[0]
                    # end condition
                    if len(keylist) == 1:
                        if isinstance(subobject, dict):
                            if key[1] == "list":
                                return subobject
                            else:
                                return None if (key[0] in subobject) else subobject
                        elif isinstance(subobject, list):
                            for asdf in subobject:
                                if key[0] not in asdf:
                                    return asdf
                            subobject.append({})
                            return subobject[-1]

                    # recursive
                    if isinstance(subobject, dict):
                        if key[0] not in subobject:
                            subobject[key[0]] = {} if key[1] != "list" else []
                        return search(subobject[key[0]], keylist[1:])
                    elif isinstance(subobject, list):
                        for obj in subobject:
                            res = search(obj, keylist[1:])
                            if res != None:
                                return res
                        subobject.append({})
                        return search(subobject[-1], keylist)

                # search start from __builtin__.json_output[__builtin__.debugid]
                subobject = search(__builtin__.json_output[__builtin__.debugid], keylist)
                key = keylist[-1]
                # restore result
                if isinstance(subobject, dict):
                    if key[1] == 'list':
                        if key[0] not in subobject:
                            subobject[key[0]] = []
                        subobject[key[0]].append(result_str)
                    else:
                        subobject[key[0]] = result_str

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
#       __builtin__.json_output[ __builtin__.debugid ]['Extras'].append( { "Type":"Int", "Value":policy } )
        return self.readString()

    @hook
    def readStrongBinder(self):
        return IBinder(self.readObject(False))

    @hook
    def readObject(self, nullMetaData):
        offset = self.offset
        self.offset += BYTE *4
        """ TODO """
        return "<<Strong binder: {}>>".format(self.data[offset: self.offset].encode('hex'))

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
        tmp = self.readInt()
#       __builtin__.json_output[ __builtin__.debugid ]['Extras'].append( { "Type":"Byte", "Value":tmp&0xff } )
        return tmp & 0xff

    @hook
    def readLong(self):
        tmp = self.readInt64()
#       __builtin__.json_output[ __builtin__.debugid ]['Extras'].append( { "Type":"Long", "Value":tmp } )
        return tmp
    @hook
    def readInt(self):
        tmp = self.readInt32()
#       __builtin__.json_output[ __builtin__.debugid ]['Extras'].append( { "Type":"Int32", "Value":tmp } )
        return tmp

    def readInt32(self):
        offset = self.offset
        self.offset += 4

        try:

            tmp =  struct.unpack("<i", self.data[offset: self.offset])[0]
            return tmp
        except struct.error as e:
            return 0
            raise IllegalParcel(e.args[0], "data[0x{:x}:0x{:x}] : {}".format(offset, self.offset, self.data[offset:self.offset].encode("hex")))

    def readInt64(self):
        offset = self.offset
        self.offset += 8
        try:
            tmp = struct.unpack("<i", self.data[offset: self.offset])[0]
            return tmp
        except struct.error as e:
            return 0
            raise IllegalParcel(e.args[0], "data[0x{:x}:0x{:x}] : {}".format(offset, self.offset, self.data[offset:self.offset].encode("hex")))

    @hook
    def readFloat(self):
        offset = self.offset
        self.offset += 4
        try:
            tmp =  struct.unpack("<f", self.data[offset: self.offset])[0]
#           __builtin__.json_output[ __builtin__.debugid ]['Extras'].append( { "Type":"Float", "Value":tmp } )
            return tmp
        except struct.error as e:
            return 0
            raise IllegalParcel(e.args[0], "data[0x{:x}:0x{:x}] : {}".format(offset, self.offset, self.data[offset:self.offset].encode("hex")))

    @hook
    def readBundle(self, loader=None):
        length = self.readInt()
        if  length < 0:
            return None
        bundle = Bundle(self, length)
#       __builtin__.json_output[ __builtin__.debugid ]['Extras'].append( { "Type":"bundle", "Value":bundle } )
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
#       __builtin__.json_output[ __builtin__.debugid ]['Extras'].append( { "Type":"String", "Value":result } )
        return result

    @hook
    def readStringArray(self):
        length = self.readInt()
        tmp =  [self.readString() for i in range(length)]
        if  0 <= length:
            return tmp
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
        if  length < 0: return None
        length += 1
        offset = self.offset
        self.offset += length*2
        self.offset = (self.offset + 3) &~ 3
        if  self.offset > len(self.data):
            raise IllegalParcel("Offset out of bound.", "from offset: 0x{:x}, get length: {}, become: {}".format(offset, length, self.offset))
        tmp = String(self.data[offset: self.offset].decode("utf16").encode("utf8").strip("\x00"))
        return tmp

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
