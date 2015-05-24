#config file

from os import path
from xml.etree import ElementTree
import os

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
    TOOLS        = path.dirname(path.abspath(__file__))
    PROJECT      = path.abspath(path.join( TOOLS , ".." ))
    _IINTERFACE  = path.abspath(path.join( PROJECT, "_IInterface" ))
    _STUB        = path.abspath(path.join( PROJECT, "_Stub" ))
    _NATIVE_STUB = path.abspath(path.join( PROJECT, "_NativeStub" ))
    OUT          = path.abspath(path.join( PROJECT, "out" ))


class System(Config):
    WORKINGDIR  = path.abspath(os.getenv("ANDROID_SDK_SRC"))
    FRAMEWORK   = path.abspath(path.join(WORKINGDIR, "frameworks"))
    JAVA_POOL   = path.abspath(path.join(WORKINGDIR, "frameworks/base/core/java/"))
    AIDL_CACHE   = path.abspath(path.join(WORKINGDIR, "out/target/common/obj/JAVA_LIBRARIES/framework_intermediates/"))

    manifest_root = ElementTree.parse(path.join(WORKINGDIR, '.repo/manifest.xml')).getroot()
    VERSION = manifest_root.find('default').attrib["revision"].split("/")[-1]
        
        

if __name__ == '__main__':
    Path().dump()
    System().dump()
