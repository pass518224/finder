class IBinder(object):
    """docstring for IBinder"""
    def __init__(self, name):
        self.name = name

    def asInterface(self, cls):
        return cls

        
