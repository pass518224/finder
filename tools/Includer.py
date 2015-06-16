import logging
from os import path
import os

logger = logging.getLogger(__name__)

SELF_CREATED = "self_created"

class Includer(object):
    def __init__(self, root, fileName):
        self.root = path.abspath(root)
        self.current = path.dirname(path.abspath(fileName))
        self.myName = fileName.split("/")[-1].split(".")[0]
        self.rPath = path.relpath(self.current, root)
        self.packages = set()
        
        self.includes = {}
        self.needSolve = set()
        self.inherits = set()
        self.instances = set()

    def setPackage(self, pkgName):
        logger.debug("set pkgname: [{}]".format(pkgName))
        self.pkgName = pkgName
        """
        if self.current != absjoin(self.root, pkgName.replace(".", "/")):
            logger.warn("dirpath: [{}]".format(self.current))
            logger.warn("pkgpath: [{}]".format(absjoin(self.root, pkgName.replace(".", "/"))))
            raise WrongPackageName
        """
        for file in os.listdir(self.current):
            if  file.endswith(".java"):
                cls = file[:-5]
                abspath = absjoin(self.current, file)
                self.packages.add(cls)
                self.include(cls, abspath)
        
    def addImport(self, pkg):
        logger.debug("import {}".format(pkg))
        cls = pkg.split(".")[-1]
        abspath = absjoin(self.root, pkg.replace(".", "/") + ".java")
        self.include(cls, pkg2path(self.root, pkg))

    def addInherit(self, mtype):
        # get last class name
        mtype = mtype.split(".")[0]

        if  mtype == self.myName:
            return
        if  mtype in self.includes:
            if  self.includes[mtype] == SELF_CREATED:
                pass
            elif  mtype not in self.needSolve and self.includes[mtype] != SELF_CREATED:
                self.needSolve.add(mtype)
                self.inherits.add(mtype)
                logger.debug("add class: {}".format(mtype))
        else:
            logger.warn("Class try to extends none included type: {}".format(mtype))
            logger.debug(self.includes)
            raise NonIncludeClass(mtype)

    def addInstance(self, mtype):
        # get last class name
        mtype = mtype.split(".")[0]

        if  mtype == self.myName:
            return
        if  mtype in self.includes:
            if  mtype not in self.needSolve and self.includes[mtype] != SELF_CREATED:
                self.needSolve.add(mtype)
                self.instances.add(mtype)
                logger.debug("add class: {}".format(mtype))

    def getInherits(self):
        result = set()
        for needed in self.inherits:
            result.add( path2pkg(self.root, self.includes[needed]))
        return result

    def getInstances(self):
        result = set()
        for needed in self.instances:
            result.add( path2pkg(self.root, self.includes[needed]))
        return result

    def summary(self):
        result = set()
        for needed in self.needSolve:
            result.add( path2pkg(self.root, self.includes[needed]))
        return result

    """
    Utilities
    """
    def include(self, cls, path):
        logger.debug("    o {:<30} => {}".format(cls, path))
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
