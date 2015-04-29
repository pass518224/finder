from os import path

class Config(object):
    def __init__(self):
        pass

    def dump(self):
        print "Class name : " + self.__class__.__name__
        for mem in [attr for attr in dir(self) if not callable(attr) and not attr.startswith("__")]:
            if  mem == "dump":
                continue
            print "{0:>12} {1}".format(mem, getattr(self, mem))

class Path(Config):
    TOOLS       = path.dirname(path.abspath(__file__))
    PROJECT     = path.abspath(path.join( TOOLS , ".." ))
    _IINTERFACE = path.abspath(path.join( PROJECT, "_IInterface" ))
    OUT         = path.abspath(path.join( PROJECT, "out" ))


class System(Config):
    WORKINGDIR  = path.abspath("/home/lucas/WORKING_DIRECTORY/")
    FRAMEWORK   = path.abspath(path.join(WORKINGDIR, "frameworks"))
        
        

if __name__ == '__main__':
    Path().dump()
    System().dump()