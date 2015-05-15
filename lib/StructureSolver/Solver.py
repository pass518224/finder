import logging
import os
import sys

from StubLoader import StubLoader

logger = logging.getLogger(__name__)

class Solver(object):
    """Solver for resolve raw format transaction data"""
    def __init__(self, stubFolderName):
        self.sLoader = StubLoader(stubFolderName)

    def solve(self, descriptor, code, data):
        if  descriptor not in self.sLoader.stubs:
            raise NoDescriptorModule("Not found descriptor: [{}]".format(descriptor))

        logger.debug("Solve [{}]/{} ".format(descriptor, code))
        onTransact = self.sLoader.stubs[descriptor].onTransact
        return onTransact(code, data, "")

class NoDescriptorModule(Exception):
    pass
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))
    os.chdir(path)
    sys.path.append(path)
    Solver("Stub")
