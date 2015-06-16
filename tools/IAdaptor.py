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
    def addImport(self, pkg):
        self.includer.addImport(pkg)

    @includerCheck
    def addInherit(self, className):
        logger.debug(" INHERIT>>> {}".format(className))
        self.includer.addInherit(className)

    @includerCheck
    def defineClass(self, cls):
        self.includer.include(cls, Includer.SELF_CREATED)

    @includerCheck
    def defineInterface(self, cls):
        self.includer.include(cls, Includer.SELF_CREATED)

    def getInherits(self):
        return self.includer.getInherits()

    @includerCheck
    def addInstance(self, className):
        self.includer.addInstance(className)
        
    def getInstances(self):
        return self.includer.getInstances()


