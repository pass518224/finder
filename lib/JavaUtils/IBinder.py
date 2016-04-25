class IBinder(object):
    """docstring for IBinder"""
    def __init__(self, name):
        self.name = name

    def asInterface(self, cls):
        return cls

    def __str__(self):
        return self.name
        
