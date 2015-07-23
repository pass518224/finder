import logging

logger = logging.getLogger(__name__)

class FilterFactory(object):
    """create filter fix the requirement"""
    def __init__(self):
        self.blacklist = set()
        self.hasCondition = False
        self.negation = False

    def addBlacklist(self, descriptor, code):
        logger.debug("{}.{}".format(descriptor, code))
        self.hasCondition=True
        self.blacklist.add((descriptor.lower(), code.lower()))

    def negate(self):
        self.negation = True

    def roleFilter(self, contain=None, sender=None, receiver=None):
        logger.debug("{}.{}.{}".format(contain, sender, receiver))

    def getFilter(self):
        if  not self.hasCondition:
            return None
        return TransactionFilter(blacklist=self.blacklist, negation=self.negation)
        

class TransactionFilter(object):
    def __init__(self, blacklist=set(), negation=False):
        self.blacklist = blacklist
        self.negation = negation
        
    def isPass(self, tra, descriptor, code):
        return self.negation ^ self._isPass(tra, descriptor, code)

    def _isPass(self, tra, descriptor, code):
        if  (descriptor.lower() ,code.lower()) in self.blacklist:
            return False
        return True
