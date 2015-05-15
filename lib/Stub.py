
class Stub(object):
    def __init__(self):
        pass

    def creatorResolver(self, *args):
        """ function call to require creator constructor for reconstruct java object from parcel raw data
        _arg0 = android.media.AudioAttributes.CREATOR.createFromParcel(data);
        to
        _arg0 = self.creatorResolver("android.media.AudioAttributes", data)
        """
        creator = args[0]
        return "creator of [{}]".format(creator)

    def interfaceResolver(self, name, strongBinder):
        """ function call of 'asInterface', ex:
        _arg3 = android.media.IAudioFocusDispatcher.Stub.asInterface(data.readStrongBinder());
        to
        _arg3 = self.interfaceResolver("android.media.IAudioFocusDispatcher", data.readStrongBinder())
        """
        return "solved interface of [{}]".format(name)

    def callFunction(self, *args, **kargs):
        return args
        
