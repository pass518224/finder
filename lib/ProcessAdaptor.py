import ProcessTable as PTable
import logging

logger = logging.getLogger(__name__)

class ProcessAdaptor(object):
    """Process adaptor
    convert dict format to processTable
    """
    def __init__(self, pTable):
        self.pTable = pTable
        self.rules = {}
        self.rules["proc_pid"] = {
                "callback": pTable.newProcess,
                "args": ["proc_pid", "name"],
            }
        self.rules["thread_pid"] = {
                "callback": pTable.newThread,
                "args": ["thread_pid", "name"],
            }
        self.rules["action"] = {
                "value": "THREAD_EXIT",
                "callback": pTable.deleteThread,
                "args": ["thread_pid"],
            }

    def action(self, info):
        matchedRule = None
        for field in self.rules:
            if  field in info:
                if  "value" not in self.rules[field]:
                    matchedRule = self.rules[field]
                    break
                elif info[field] == self.rules[field]["value"]:
                    matchedRule = self.rules[field]
                    break

        if  matchedRule is None:
            raise UnknownRule

        args = []
        for key in matchedRule["args"]:
            args.append(info[key])
        matchedRule["callback"](*args)

class UnknownRule(Exception):
    """Can't find matched rule'"""
    pass
        
if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    p = ProcessAdaptor(PTable.ProcessTable() )
