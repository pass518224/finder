import logging
import binascii
import string
import struct

logger = logging.getLogger(__name__)

class Parcel(object):
    """Parcel object to contain data"""
    def __init__(self, hex):
        super(Parcel, self).__init__()
        self.data = binascii.unhexlify(hex)
        self.offset = 0

    def readInt(self):
        return self.readInt32()

    def readInt32(self):
        offset = self.offset
        self.offset += 4
        return struct.unpack("<i", self.data[offset: self.offset])[0]
        
    def readString(self):
        return self.readString16()

    def readString16(self):
        length = self.readInt32()
        offset = self.offset
        self.offset += length*2
        return self.data[offset: self.offset]

    def getDescriptor(self):
        try:
            length = struct.unpack("<i", self.data[4: 8])[0]
        except struct.error as e:
            raise IllegalParcel(e)
        return ''.join([i if 31 < ord(i) < 127 else '' for i in self.data[8: 8+length*2]])
    
    def __str__(self):
        return ''.join([i if 31 < ord(i) < 127 else '.' for i in self.data])

    def __repr__(self):
        return "'<Parcel Object: " + ''.join([i if 31 < ord(i) < 127 else '' for i in self.data]) + ">'"
        
class IllegalParcel(Exception):
    pass

if __name__ == '__main__':
    #hex = "870b00002000000061006e00640072006f00690064002e006e00650074002e0049004e006500740077006f0072006b0053007400610074007300530065007200760069006300650000000000"
    hex = "2000000061006600640072006f00690064002e006e00650074002e0049004e006500740077006f0072006b0053007400610074007300530065007200760069006300650000000000"
    p = Parcel(hex)
    print p
    id = p.readString16()
    print
    if  id is "afdroid.net.INetworkStatsService".encode("utf8"):
        print id
