#config loader

from os import path
from xml.etree import ElementTree
import os

def absjoin(*args):
    return path.abspath(path.join(*args))

class Config(object):
    def __init__(self):
        pass

    def dump(self):
        print "Class name : " + self.__class__.__name__
        for mem in [attr for attr in dir(self) if not callable(attr) and not attr.startswith("__")]:
            if  mem == "dump":
                continue
            print "{0:>12} {1}".format(mem, getattr(self, mem))

class PathInfo(Config):
    TOOLS        = path.dirname(path.abspath(__file__))
    PROJECT      = path.abspath(path.join( TOOLS , ".." ))
    _IINTERFACE  = path.abspath(path.join( PROJECT, "_IInterface" ))
    _HARDWARE    = path.abspath(path.join( PROJECT, "_Hardware" ))
    _STUB        = path.abspath(path.join( PROJECT, "_Stub" ))
    _NATIVE_STUB = path.abspath(path.join( PROJECT, "_NativeStub" ))
    OUT          = path.abspath(path.join( PROJECT, "out" ))
    CREATOR      = path.abspath(path.join( PROJECT, "out/android-5.1.1_r1/java" ))
    MODULE       = path.abspath(path.join( PROJECT, "modules" ))
    EVAL         = path.abspath(path.join( OUT, "evaluation" ))

class SystemInfo(Config):
    def __init__(self, workingdir=None):
        self.WORKINGDIR     = workingdir
        if  workingdir:
            self.configure()

    def configure(self):
        self.FRAMEWORK      = path.abspath(path.join(self.WORKINGDIR, "frameworks"))
        self.SYSTEM         = path.abspath(path.join(self.WORKINGDIR, "system"))
        self.PACKAGES       = path.abspath(path.join(self.WORKINGDIR, "packages"))
        self.LIBCORE        = path.abspath(path.join(self.WORKINGDIR, "libcore/luni/src/main/java/libcore/"))
        self.LIBJAVA        = path.abspath(path.join(self.WORKINGDIR, "libcore/luni/src/main/java/java/"))
        self.JAVA_POOL      = path.abspath(path.join(self.WORKINGDIR, "frameworks/base/core/java/"))
        self.JAVA_GRAPHIC   = path.abspath(path.join(self.WORKINGDIR, "frameworks/base/graphics/java/"))
        self.JAVA_TELECOMM  = path.abspath(path.join(self.WORKINGDIR, "frameworks/base/telecomm/java/"))
        self.JAVA_TELEPHONY = path.abspath(path.join(self.WORKINGDIR, "frameworks/base/telephony/java/"))
        self.JAVA_MEDIA     = path.abspath(path.join(self.WORKINGDIR, "frameworks/base/media/java/"))
        self.JAVA_LOCATION  = path.abspath(path.join(self.WORKINGDIR, "frameworks/base/location/java/"))
        self.JAVA_LIBS      = [self.JAVA_POOL, self.JAVA_GRAPHIC, self.JAVA_TELECOMM, self.JAVA_TELEPHONY, self.JAVA_MEDIA, self.JAVA_LOCATION]
        self.AIDL_CACHE     = path.abspath(path.join(self.WORKINGDIR, "out/target/common/obj/JAVA_LIBRARIES/"))

        manifest_root = ElementTree.parse(path.join(self.WORKINGDIR, '.repo/manifest.xml')).getroot()
        self.VERSION= manifest_root.find('default').attrib["revision"].split("/")[-1]

    def setVersion(self, version):
        self.VERSION = version

def parse(fd):
    raw = fd.read()
    result = {}

    count = 0
    for line in raw.split("\n"):
        count += 1
        if  line.startswith("#"):
            continue
        if  len(line) > 0:
            line = line.strip(' ')
            try:
                key, val = line.split("=")
            except:
                raise Exception("Must satisfy format [key]=[val], error at line: {}".format(count))
            result[key] = val
    return result

Path = PathInfo()

with open(absjoin(Path.PROJECT, "config"), "r") as configFd:
    config = parse(configFd)

if "VERSION" in config:
    System = SystemInfo()
    System.setVersion(config["VERSION"])
elif  "ANDROID_SDK_SRC" in config:
    System = SystemInfo(workingdir=config["ANDROID_SDK_SRC"])
else:
    raise Exception("undecided version or android source path")
        

DEBUG = False
NOT_SOLVE = False
JSONOUTPUT = None

if __name__ == '__main__':
    Path.dump()
    System.dump()
