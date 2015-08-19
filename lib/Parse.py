import logging
import re
from collections import Iterator

logger = logging.getLogger(__name__)

UNKNOWN = -1
INFO = "INFO"
WRITE_READ = "WRITE_READ"
BC_TRANSACTION = "BC_TRANSACTION"
BC_REPLY = "BC_REPLY"



class Parser(Iterator):
    """Parser for logger data
        Iterate the parser, the parser return flag of fetched data type.
        The parsed data can be got by `getInfo()`.
    """
    def __init__(self, fd):
        self.fd = fd

        self._finder = "Finder> "
        self._write_read = "WRITE_READ"
        self._bc_transaction = "BC_TRANSACTION"
        self._bc_reply = "BC_REPLY"
        self.lineno = 0

    def next(self):
        """
        read line of file

        @return: flag for this raw type
        """
        self.raw = None
        self.info = None

        while True:
            raw = self.fd.readline()[:-1];
            self.lineno += 1
            if len(raw) is 0:   #EOF catched
                self.fd.close()
                raise StopIteration

            offset = raw.find(self._finder)
            if  offset < 0: # Not the type of Finder project
                continue

            raw = raw[offset + len( self._finder):]  # stripe "Finder> " prefix

            #parse the format
            if  raw[0] is "[":  # system related infomation
                if  raw.find("Error dump:") > 0:
                    offset = raw.find("Error dump:")
                    raw = raw[:offset] + "Error_dump_sys]"

                flag = INFO
                info = infoCreator(raw)
                self.info = info
                self.raw = raw
                break

            elif raw.find(self._write_read) >= 0:
                flag = WRITE_READ
                type = None
                if raw.find(self._bc_transaction) >= 0:
                    offset = raw.find(self._bc_transaction) + len(self._bc_transaction) + 1 # " [" to shift
                    raw = raw[offset:]
                    type = BC_TRANSACTION
                elif raw.find(self._bc_reply) >= 0:
                    offset = raw.find(self._bc_reply) + len(self._bc_reply) + 1 # " [" to shift
                    raw = raw[offset:]
                    type = BC_REPLY
                else:
                    offset = raw.find(self._write_read) + len(self._write_read) + 1
                    logger.warn("unknown readable raw type {}.{} ...".format(self._write_read, raw[offset:offset+10]))
                    continue
                
                info = infoCreator(raw)
                if  "length" in info and info["length"] == "0":
                    continue
                info["type"] = type

                self.info = info
                self.raw  = raw
                break

            else:
                flag = UNKNOWN
                break

        return flag
        
    def getRaw(self):
        """get raw data of line"""
        return self.raw

    def getInfo(self):
        """return parsed data with dict type data structure"""
        return self.info
    
    def getDebug(self):
        return {"raw" : self.raw, "lineno" : self.lineno}

def infoCreator(raw_info):
    """
        create info object come from raw_info

        @raw_info: ex [code: 100, name: lucas]
        @return: dict -> [key: value]
    """
    attrs = raw_info[1:-1].split(", ")
    info = {}
    for attr in attrs:
        try:
            key, val = attr.split(": ")
        except ValueError:
            logger.warn("seperate error: " + attr)
        info[key] = val
        
    return info

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    with open("sample/kmsg.short", "r") as fd:
        p = Parser(fd)
        for flag in p:
            print p.getDebug()
    
