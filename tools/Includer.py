import logging
from os import path
import os

import Config

logger = logging.getLogger(__name__)

SELF_CREATED = "self_created"

class Includer(object):
    def __init__(self, root, fileName):
        self.root = path.abspath(root)
        self.current = path.dirname(path.abspath(fileName))
        self.myName = fileName.split("/")[-1].split(".")[0]
        self.rPath = path.relpath(self.current, root)
        self.packages = ""
        
        self.includes = {}
        self.needSolve = set()
        self.inherits = set()

    def setPackage(self, pkgName):
        logger.debug("set pkgname: [{}]".format(pkgName))
        self.pkgName = pkgName
        for file in os.listdir(self.current):
            if  file.endswith(".java"):
                cls = file[:-5]
                if  cls != self.myName:
                    abspath = absjoin(self.current, file)
                    self.packages = cls
                    self.include(cls, abspath)
        
    def addImport(self, pkg, isStatic):
        if  isStatic:
            pkg = ".".join(pkg.split(".")[:-1])

        if  not (pkg.split(".")[0] == "libcore" or pkg.split(".")[0] == "java" or isExistFile(pkg)):
            return

        logger.debug("import {}".format(pkg))
        cls = pkg.split(".")[-1]
        abspath = absjoin(self.root, pkg.replace(".", "/") + ".java")
        self.include(cls, pkg2path(self.root, pkg))

    def addInherit(self, mtype):
        # get last class name
        mtype = mtype.split(".")[0]

        if  mtype == self.myName:
            return
        if  mtype == "Exception":
            return
        if  mtype in self.includes:
            self.inherits.add(mtype)
            logger.debug("add class: {}".format(mtype))
        else:
            raise NonIncludeClass("Class try to extends none included type: {}".format(mtype))

    def getInherits(self):
        result = set()
        for needle in self.inherits:
            result.add(path2pkg(self.root, self.includes[needle]))
        return result

    def getMore(self, pkgNames):
        total = set(self.includes)
        result = set()
        for needle in (total & pkgNames):
            result.add(path2pkg(self.root, self.includes[needle]))
        return result

    def getUsedPkgs(self, usedName):
        total = set(self.includes)
        instances = (total - self.inherits) & usedName
        if self.myName in instances:
            instances.remove(self.myName)
        result = set()
        for needle in instances:
            result.add(path2pkg(self.root, self.includes[needle]))
        return result

    def summary(self, usedName):
        pass

    """
    Utilities
    """
    def include(self, cls, path):
        logger.debug("    o {:<30} => {}".format(cls, path))
        self.includes[cls] = path

def path2pkg(root, file):
    rel = path.relpath(file, root)
    if  not rel.endswith(".java"):
        raise Exception("not a valid file path:\n\t{}/{}".format(root, file))
    return rel[:-5].replace("/", ".")

def pkg2path(root, pkg):
    return root + "/" + pkg.replace(".", "/") + ".java"

def absjoin(*args):
    return path.abspath(path.join(*args))

def isExistFile(pkg):
    sourcePool = Config.System.JAVA_LIBS
    for source in sourcePool:
        file = pkg2path(source, pkg)
        if  os.path.isfile(file):
            return True
    return False


class WrongPackageName(Exception):
    pass

class NonIncludeClass(Exception):
    pass

if __name__ == '__main__':
    root = "/Volumes/android/sdk-source-5.1.1_r1/frameworks/base/core/java"
    file = root + "/android/content/pm/PackageInfo.java"
    includer = Includer(root, file)
    print  pkg2path(root, "os.content.Parcel")
