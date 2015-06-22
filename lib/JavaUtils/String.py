class String(str):
    """docstring for String"""
    def __init__(self, *args):
        super(String, self).__init__(*args)
        self.__class__.__name__ = "str"
        

    def obtain(self):
        return 

    def intern(self):
        return 
        
