import Parcel
import sys

class BaseBundle(object):
    """docstring for BaseBundle"""
    def __init__(self, parcel, length):
        self.mParcelledData = None
        self.mClassLoader = None
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
        self.mMap = {}

    def setClassLoader(self, loader):
        self.loader = loader

    def unparcel(self):
        if  self.mParcelledData == None:
            return

        N = self.mParcelledData.readInt()

        if  N < 0:
            return

        self.mParcelledData.readArrayMapInternal(self.mMap, N, self.mClassLoader)

    def __str__(self):
        try:
            self.unparcel()
            return str(self.mMap)
        except:
            return str(self.mMap) + "... unsolved"
