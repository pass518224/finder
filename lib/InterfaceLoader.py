import logging
import os
import json

logger = logging.getLogger(__name__)

class InterfaceLoader(object):
    def __init__(self, dirPath):
        self.dirPath = dirPath
        self.descriptors = {}

        for filename in os.listdir(self.dirPath):
            logger.debug("loading file: [{}]...".format(filename))
            logger.debug(type(filename))
            self.descriptors[filename] = {}
            cPath = os.path.join(self.dirPath, filename)
            for val, key in json.load(file(cPath), encoding = "utf8")["data"].items():
                self.descriptors[filename][str(key)] = val.encode("utf8")

    def getCode(self, descriptor, code):
        """ debug usage
        if  descriptor not in self.descriptors:
            print "not found des = " + descriptor
        elif code not in self.descriptors[descriptor]:
            print "not found code = " + code
        else:
            print 
        """
        try:
            return self.descriptors[descriptor][code]
        except:
            raise NoneExistCode
        

class NoneExistCode(Exception):
    pass
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    iLoader = InterfaceLoader("/home/lucas/WORKING_DIRECTORY/kernel/goldfish/Finder/out/interface/")
    if  "android.content.IContentService" in iLoader.descriptors:
        print "yes"
