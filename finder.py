#! /usr/bin/env python2.7
import logging
import os

import lib.Parse as Parse
import lib.ProcessTable as PTable
import lib.ProcessAdaptor as PAdaptor
import lib.TransactionManager as TrManager
import lib.Transaction as Transaction

import lib.InterfaceLoader as ILoader

import tools.Config as Config

def finder():
    """entry function"""
    fd = open("/home/lucas/Downloads/syslog/kmsg.sample", "r")
    sys_log = Parse.Parser(fd)

    #process related
    pTable = PTable.ProcessTable()
    pAdaptor = PAdaptor.ProcessAdaptor(pTable)

    #loaders
    iLoader = ILoader.InterfaceLoader(os.path.join(Config.Path.OUT, "interface"))


    #transaction manger
    tManager = TrManager.TransactionManager(pTable, iLoader)

    for flag in sys_log:
        if flag == Parse.INFO:
            # handle system INFO
            info = sys_log.getInfo()
            try:
                pAdaptor.action(info)
            except PAdaptor.UnknownRule:
                logging.warn("unknown rule: " + str(info))
        elif flag == Parse.WRITE_READ:
            try:
                tManager.addTransaction( Transaction.Transaction(sys_log.getInfo()) )
            except Transaction.TransactionError as e:
                logger.warn("transaction error: " + e.args[0])

    tManager.dump()

    #pTable.dumpTable()

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    logger = logging.getLogger(__name__)
    finder()
