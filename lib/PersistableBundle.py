BUNDLE_MAGIC = 0x4C444E42
class BaseBundle(object):
    """docstring for BaseBundle"""
    def __init__(self, parcel, length):
        self.readFromParcelInner(parcel, length)

    def readFromParcelInner(self, parcel, length):
        if  length == 0:
            self.mParcelledData = "EMPTY_PARCEL"
            return

        magic = parcel.readInt()
        if  magic != BUNDLE_MAGIC:
            pass
            # throw throw new IllegalStateException("Bad magic number for Bundle: 0x"  + Integer.toHexString(magic));

        parcel.offset = parcel.offset + length
        

class PersistableBundle(BaseBundle):
    """docstring for PersistableBundel"""
    def __init__(self, parcel, length):
        super(PersistableBundle, self).__init__(parcel, length)
        
