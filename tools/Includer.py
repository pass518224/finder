import logging
from os import path
import os

logger = logging.getLogger(__name__)

class Includer(object):
    def __init__(self, root, fileName):
        self.root = path.abspath(root)
        self.current = path.dirname(path.abspath(fileName))
        self.rPath = path.relpath(self.current, root)
        self.packages = set()
        
        self.includes = {}
        self.needSolve = set()

    def setPackage(self, pkgName):
        logger.debug("set pkgname: [{}]".format(pkgName))
        self.pkgName = pkgName
        if self.current != absjoin(self.root, pkgName.replace(".", "/")):
            logger.warn("dirpath: [{}]".format(self.current))
            logger.warn("pkgpath: [{}]".format(absjoin(self.root, pkgName.replace(".", "/"))))
            raise WrongPackageName
        for file in os.listdir(self.current):
            if  file.endswith(".java"):
                cls = file[:-5]
                abspath = absjoin(self.current, file)
                self.packages.add(cls)
                self.include(cls, abspath)
        
    def addImport(self, pkg):
        logger.debug("import {}".format(path))
        cls = pkg.split(".")[-1]
        abspath = absjoin(self.root, pkg.replace(".", "/") + ".java")
        self.include(cls, pkg2path(self.root, pkg))

    def addType(self, mtype):
        mtype = mtype.split(".")[0]
        if  mtype in self.includes:
            logger.debug("add class: {}".format(mtype))
            self.needSolve.add(mtype)
        else:
            logger.warn("Not included type: {}".format(mtype))
            #raise NonIncludeClass("type: {}".format(mtype))

    def summary(self):
        result = set()
        for needed in self.needSolve:
            """
            if  needed in self.packages:
                result.add(needed)
            else:
                result.add( path2pkg(self.root, self.includes[needed]))
            """
            result.add( path2pkg(self.root, self.includes[needed]))
        return result

    """
    Utilities
    """
    def include(self, cls, path):
        logger.debug(">> include {:<30} => {}".format(cls, path))
        self.includes[cls] = path

def path2pkg(root, file):
    rel = path.relpath(file, root)
    if  not rel.endswith(".java"):
        raise Exception("not a valid file path")
    return rel[:-5].replace("/", ".")

def pkg2path(root, pkg):
    return root + "/" + pkg.replace(".", "/") + ".java"

def absjoin(*args):
    return path.abspath(path.join(*args))

class WrongPackageName(Exception):
    pass

class NonIncludeClass(Exception):
    pass

if __name__ == '__main__':
    root = "/Volumes/android/sdk-source-5.1.1_r1/frameworks/base/core/java"
    file = root + "/android/content/pm/PackageInfo.java"
    includer = Includer(root, file)
    print  pkg2path(root, "os.content.Parcel")
