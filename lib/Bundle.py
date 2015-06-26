class BaseBundle(object):
    """docstring for BaseBundle"""
    def __init__(self, parcel, length):
        self.readFromParcelInner(parcel, length)

    def readFromParcelInner(self, parcel, length):
        if  length == 0:
            mParcelledData = "empty_parcel"

        magic = parcel.readInt();
        parcel.offset += length
        """ TODO """
        

class Bundle(BaseBundle):
    """docstring for Bundle"""
    def __init__(self, parcel, length):
        super(self.__class__, self).__init__(parcel, length)

    def setClassLoader(self, loader):
        self.loader = loader
