import logging
import sys
import os
import pkgutil
import json

logger = logging.getLogger(__name__)

class StubLoader(object):
    """docstring for TransactionLoader"""
    def __init__(self, stubFolderName, loadOnly = None):
        self.stubFolderName = stubFolderName
        self.package = stubFolderName
        self.stubs = {}
        count = 0
        if  loadOnly is not None:
            for module in loadOnly:
                descriptor, instance = self.loadStubModule(module)
                self.stubs[descriptor] = instance
                count += 1
        else: # load all modules
            for module_loader, name, ispkg in pkgutil.iter_modules([stubFolderName]):
                descriptor, instance = self.loadStubModule(name)
                self.stubs[descriptor] = instance
                count += 1
        logger.info("Total load in {} modules".format(count))

    def loadStubModule(self, name):
        _from   = "{}.{}".format(self.package, name)
        _import = name
        module  = __import__(_from, globals(), locals(), [_import])
        instance = module.OnTransact()
        descriptor = instance.descriptor if hasattr(instance, "descriptor") else instance.DESCRIPTOR
        logger.debug("Load in: [{}] = {}".format( descriptor, _from))
        return descriptor, instance

class Property(object):
    pass

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)

    sloader = StubLoader("Stubs")
