import logging
import Includer

logger = logging.getLogger(__name__)

class IncludeAdaptor(object):
    """
    Adapt from compiler to includer for decoupleing
    """
    def __init__(self, includer=None):
        self.includer = includer

    def setIncluder(self, includer):
        self.includer = includer

    def includerCheck(func):

        def checker(*args, **kargs):
            if  not args[0].includer:
                return False
            result = func(*args, **kargs)
            return result

        return checker

    def setIncluder(self, includer):
        self.includer = includer

    @includerCheck
    def setPackage(self, pkg):
        self.includer.setPackage(pkg)

    @includerCheck
    def addImport(self, pkg, isStatic):
        self.includer.addImport(pkg, isStatic)

    @includerCheck
    def addInherit(self, className):
        logger.debug(" INHERIT>>> {}".format(className))
        self.includer.addInherit(className)

    @includerCheck
    def getInherits(self):
        return self.includer.getInherits()

    @includerCheck
    def getMore(self, pkgNames):
        return self.includer.getMore(pkgNames)

    @includerCheck
    def summary(self):
        return self.includer.summary()

