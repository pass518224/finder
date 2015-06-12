import logging
import Includer

logger = logging.getLogger(__name__)

class IncludeAdaptor(object):
    """
    Adapt from compiler to includer for decoupleing
    """
    def __init__(self, includer=None):
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
        self.includer.addType(className)

    @includerCheck
    def addInstance(self, className):
        try:
            self.includer.addType(className)
        except Includer.NonIncludeClass as e:
            pass
        

