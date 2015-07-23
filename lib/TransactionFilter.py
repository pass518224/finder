import logging

logger = logging.getLogger(__name__)

class FilterFactory(object):
    """create filter fix the requirement"""
    def __init__(self):
        self.blacklist = set()
        self.negation = False

        self.permitSender = set()
        self.permitReceiver = set()

    def addBlacklist(self, descriptor, code):
        logger.debug("{}.{}".format(descriptor, code))
        self.blacklist.add((descriptor.lower(), code.lower()))

    def negate(self):
        self.negation = True

    def roleFilter(self, contain=None, sender=None, receiver=None):
        if  contain:
            self.permitSender.add(contain)
            self.permitReceiver.add(contain)
        if  sender:
            self.permitSender.add(sender)
        if  receiver:
            self.permitReceiver.add(receiver)

    def getFilter(self):
        return TransactionFilter(blacklist=self.blacklist, negation=self.negation, senders=self.permitSender, receivers=self.permitReceiver)
        

class TransactionFilter(object):
    def __init__(self, blacklist=set(), negation=False, senders=None, receivers=None):
        self.blacklist = blacklist
        self.negation = negation
        self.senders = senders
        self.receivers = receivers
        
    def isPass(self, tra, descriptor, code):
        return self.negation ^ self._isPass(tra, descriptor, code)

    def _isPass(self, tra, descriptor, code):
        if  (descriptor.lower() ,code.lower()) in self.blacklist:
            return False

        if  self.senders or self.receivers:
            if not (tra.from_proc_name in self.senders or tra.to_proc_name in self.receivers):
                return False
        return True
