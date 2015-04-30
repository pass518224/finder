import logging

logger = logging.getLogger(__name__)

PROCESS = "process"
THREAD = "thread"

class ProcessTable(object):
    """Process table for recording infomation of process and thread"""
    def __init__(self):
        self.table = {}

    def newProcess(self, pid, name):
        logger.debug("new proc:{0}[{1}]".format(pid, name))
        self.table[pid] = {
                "name": name,
                "type": PROCESS
            }

    def newThread(self, tid, name):
        logger.debug("new thread:{0}[{1}]".format(tid, name))
        self.table[tid] = {
                "name": name,
                "type": THREAD
            }

    def deleteThread(self, tid):
        logger.debug("del thread:{0}".format(tid))
        if  tid in self.table:
            del self.table[tid]
        else:
            logger.warn("delete unused thread:[{0}]".format(tid))

    def getNameFromPid(self, pid):
        if  type(pid) == int:
            pid = str(pid)

        if  pid not in self.table:
            raise NoneExistPid
        
        return (self.table[pid]["name"], self.table[pid]["type"])

    def dumpTable(self):
        for node in self.table:
            print "      {0:>5s}  [{2}]{1:<40s}".format(node, self.table[node]["name"], self.table[node]["type"][0])

class NotEqualInt(Exception):
    pass
        
class NoneExistPid(Exception):
    pass
        
