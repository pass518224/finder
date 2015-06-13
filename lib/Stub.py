import logging

logger = logging.getLogger(__name__)

class Stub(object):
    def __init__(self):
        pass

    def creatorResolver(self, name, *args):
        """ function call to require creator constructor for reconstruct java object from parcel raw data
        _arg0 = android.media.AudioAttributes.CREATOR.createFromParcel(data);
        to
        _arg0 = self.creatorResolver("android.media.AudioAttributes", data)
        """
        import sys
        sys.path.append("/Users/lucas/finder/Creators")

        className = name.split(".")[-1]
        try:
            creator = __import__(name, globals(), locals(), className)
            getattr(creator, className).CREATOR.createFromParcel(*args)
        except ImportError as e:
            logger.warn(e)
            return "Unfound creator"

        return "creator of [{}]".format(creator)

    def interfaceResolver(self, name, strongBinder):
        """ function call of 'asInterface', ex:
        _arg3 = android.media.IAudioFocusDispatcher.Stub.asInterface(data.readStrongBinder());
        to
        _arg3 = self.interfaceResolver("android.media.IAudioFocusDispatcher", data.readStrongBinder())
        """
        return "solved interface of [{}]".format(name)

    def newInstance(self, name, *args):
        print name
        raise CallCreator("new instance")
        """docstring for newInstance"""
        pass

    def callFunction(self, funName, *args, **kargs):
        return "{}({})".format(funName, ", ".join(str(i) for i in args))
       
class CallCreator(Exception):
    pass
