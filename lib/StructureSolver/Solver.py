import logging
import os
import sys
import traceback

from StubLoader import StubLoader
import lib.Parcel as Parcel
import lib.Stub   as Stub

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
        try:
            return onTransact(code, data, Parcel.Parcel(""))
        except Parcel.IllegalParcel as e:
            print descriptor, code
            print data
            logger.warn(e)
            traceback.print_exc()
        except Parcel.NoneImplementFunction as e:
            logger.warn(e)
        except Stub.CallCreator as e:
            logger.warn(e)
        except:
            print traceback.format_exc()

class NoDescriptorModule(Exception):
    pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    """
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))
    os.chdir(path)
    sys.path.append(path)
    """
    Solver("Stub")
