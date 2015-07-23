import logging
from collections import defaultdict

import ProcessTable
import Parcel
import InterfaceLoader

logger = logging.getLogger(__name__)

hardwareDescriptors = [
    "android.net.INetworkStatsService",
    "android.gui.IGraphicBufferProducer",
    "android.gui.DisplayEventConnection",
    "android.ui.ISurfaceComposer",
    "android.ui.ISurfaceComposerClient",
    "android.gui.IProducerListener",
    "android.media.IAudioFlinger",
    "android.media.IAudioFlingerClient",
    "android.media.IAudioPolicyService",
    "android.media.IMediaPlayerService",
    "android.utils.IMemoryHeap",
    "android.ui.IGraphicBufferAlloc",
    "android.media.IAudioTrack",
    "android.utils.IMemory",
    "android.hardware.ISoundTriggerHwService",
    "drm.IDrmManagerService",
    "android.media.IMediaMetadataRetriever"
]

DISCOVERED = "DISCOVERED"
SOLVED = "SOLVED"

UNKNOWN_NAME = "[????]"


class TransactionManager(object):
    """manage trnasactions, resolve and print out"""
    def __init__(self, processTable, interfaceLoader, structureSolver = None):
        self.processTable = processTable
        self.iLoader = interfaceLoader

        self.transactions = []
        if  structureSolver is not None:
            self.sSolver = structureSolver

        self.solvingTable = defaultdict(dict)
        self.total = 0
        self.solved = 0
        self.eTotal = 0
        self.eSolved = 0

        self.filter = None

        self.missedTransaction = defaultdict(set)

    def addTransaction(self, transaction):
        try:
            (pName, pType) = self.processTable.getNameFromPid(transaction.from_proc)
            setattr(transaction, "from_proc_name", pName)
        except ProcessTable.NoneExistPid:
            setattr(transaction, "from_proc_name", UNKNOWN_NAME)
        try:
            (tName, tType) = self.processTable.getNameFromPid(transaction.from_thread)
            setattr(transaction, "from_thread_name", tName)
        except ProcessTable.NoneExistPid:
            setattr(transaction, "from_thread_name", UNKNOWN_NAME)
        try:
            (fName, fType) = self.processTable.getNameFromPid(transaction.to_proc)
            setattr(transaction, "to_proc_name", fName)
        except ProcessTable.NoneExistPid:
            setattr(transaction, "to_proc_name", UNKNOWN_NAME)
        self.transactions.append(transaction)
        
    def registFilter(self, filter):
        self.filter = filter

    def solve(self, tra):
        if  tra.type == "BC_TRANSACTION":
            try:
                descriptor = tra.parcel.getDescriptor()
            except Parcel.IllegalParcel as e:
                logger.info(tra)
                logger.warn(e.args[0])
                return

            if  descriptor in hardwareDescriptors:
                return
            try:
                code = self.iLoader.getCode(descriptor, tra.code)
                if  self.filter and not self.filter.isPass(tra, descriptor, code):
                    return
                self.eTotal += 1
                if  descriptor in self.solvingTable and code in self.solvingTable[descriptor] and self.solvingTable[descriptor][code] == SOLVED:
                    pass
                elif descriptor in self.solvingTable and code in self.solvingTable[descriptor] and self.solvingTable[descriptor][code] == DISCOVERED:
                    pass
                else:
                    self.total += 1
                    self.solvingTable[descriptor][code] = DISCOVERED
                print "=============================="
                print "#{} {} ==> {} / [{}]: {}".format(tra.debug_id, tra.from_proc_name, tra.to_proc_name, descriptor, code)
                print "{{{"
                result = self.sSolver.solve(descriptor, code, tra.parcel)
                if  result:
                    self.eSolved += 1
                    if  self.solvingTable[descriptor][code] != SOLVED:
                        self.solved += 1
                        self.solvingTable[descriptor][code] = SOLVED
                    print "}}}"
                    print "\t" + result
                else:
                    print "}}}"
            except InterfaceLoader.NoneExistCode as e:
                print "}}}"
                self.missedTransaction[descriptor].add(tra.code)
        """
        else:
            print tra
        """

    def getMissedTransaction(self):
        result = "\n"
        for descriptor, codes in self.missedTransaction.items():
            result += "[{}]:{}\n".format(descriptor, ", ".join(str(i) for i in codes))
        return result

