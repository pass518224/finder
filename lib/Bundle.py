import Parcel
class BaseBundle(object):
    """docstring for BaseBundle"""
    def __init__(self, parcel, length):
        self.readFromParcelInner(parcel, length)

    def readFromParcelInner(self, parcel, length):
        if  length == 0:
            mParcelledData = "empty_parcel"

        magic = parcel.readInt();
        offset = parcel.offset
        parcel.offset += length
        p = Parcel.Parcel("")
        p.setData(parcel.data[offset:offset+length])
        
        self.mParcelledData = p
        """
        print parcel.hexdump()
        print p.hexdump()
        """
        

class Bundle(BaseBundle):
    """docstring for Bundle"""
    def __init__(self, parcel, length):
        super(self.__class__, self).__init__(parcel, length)

        self.mHasFds = self.mParcelledData.hasFileDescriptors()
        self.mFdsKnown = True

    def setClassLoader(self, loader):
        self.loader = loader
