import logging
import ProcessTable

logger = logging.getLogger(__name__)

class TransactionManager(object):
    """manage trnasactions, resolve and print out"""
    def __init__(self, processTable, interfaceLoader):
        self.processTable = processTable
        self.iLoader = interfaceLoader

        self.transactions = []

    def addTransaction(self, transaction):
        try:
            (pName, pType) = self.processTable.getNameFromPid(transaction.from_proc)
            setattr(transaction, "from_proc_name", pName)
        except ProcessTable.NoneExistPid:
            setattr(transaction, "from_proc_name", "[????]")
        try:
            (tName, tType) = self.processTable.getNameFromPid(transaction.from_thread)
            setattr(transaction, "from_thread_name", tName)
        except ProcessTable.NoneExistPid:
            setattr(transaction, "from_thread_name",  "[????]")
        try:
            (fName, fType) = self.processTable.getNameFromPid(transaction.to_proc)
            setattr(transaction, "to_proc_name", fName)
        except ProcessTable.NoneExistPid:
            setattr(transaction, "to_proc_name", "[????]")
        self.transactions.append(transaction)


    def dump(self):
        for tra in self.transactions:
            print tra.from_proc, tra.from_proc_name,  tra.from_thread_name
        
