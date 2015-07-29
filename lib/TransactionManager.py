import logging
from datetime import datetime
from collections import defaultdict

import ProcessTable
import Parcel
import InterfaceLoader
import Module

import tools.Config as Config

logger = logging.getLogger(__name__)

hardwareDescriptors = [
    #"android.net.INetworkStatsService",
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

    def lookup(self, tra):
        try:
            descriptor = tra.parcel.getDescriptor()
        except Parcel.IllegalParcel as e:
            #logger.info(tra)
            #logger.warn(e.args[0])
            raise LookupException("lookup descriptor fail: {}".format(e.args[0]))

        if  descriptor in hardwareDescriptors:
            raise HardwareDescriptor()

        try:
            code = self.iLoader.getCode(descriptor, tra.code)
        except InterfaceLoader.NoneExistCode as e:
            self.missedTransaction[descriptor].add(tra.code)
            raise LookupException("none exist code with {}:{}".format(descriptor, tra.code))
        return descriptor, code

    def list(self):
        for tra in self.transactions:
            if  tra.type == "BC_TRANSACTION":
                try:
                    descriptor, code = self.lookup(tra)
                except:
                    continue
                if  self.filter and not self.filter.isPass(tra, descriptor, code):
                    continue
                print ",".join(str(i) for i in [tra.time, tra.debug_id, tra.from_proc_name, tra.to_proc_name, descriptor, code])
        

    def solve(self, tra):
        if  tra.type == "BC_TRANSACTION":
            try:
                descriptor, code = self.lookup(tra)
            except LookupException as e:
                #logger.warn(e)
                return 
            except HardwareDescriptor:
                return

            if  self.filter and not self.filter.isPass(tra, descriptor, code):
                return

            Module.getModule().call("SOLVING_START", tra, descriptor, code)


            if  not Config.NOT_SOLVE:
                print "=============================="
                #print "#{}[{}] {} ==> {} / [{}]: {}".format(tra.debug_id, datetime.fromtimestamp(tra.time).strftime('%Y-%m-%d %H:%M:%S'), tra.from_proc_name, tra.to_proc_name, descriptor, code)
                print "#{} {} ==> {} / [{}]: {}".format(tra.debug_id, tra.from_proc_name, tra.to_proc_name, descriptor, code)
                #print "{{{"
                result = self.sSolver.solve(descriptor, code, tra.parcel)
                #print "}}}"

                if  result:
                    print "\t{}({})".format(result[0], ", ".join(str(i) for i in result[1:]))
                    Module.getModule().call("SOLVING_SUCCESS", *result)
                else:
                    Module.getModule().call("SOLVING_FAIL")
        """
        else:
            print tra
        """

    def getMissedTransaction(self):
        result = "\n"
        for descriptor, codes in self.missedTransaction.items():
            result += "[{}]:{}\n".format(descriptor, ", ".join(str(i) for i in codes))
        return result

class LookupException(Exception):
    pass

class HardwareDescriptor(Exception):
    pass

