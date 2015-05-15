#! /usr/bin/env python2.7
import logging
import os

import lib.Parse as Parse
import lib.ProcessTable as PTable
import lib.ProcessAdaptor as PAdaptor
import lib.TransactionManager as TrManager
import lib.Transaction as Transaction

import lib.InterfaceLoader as ILoader
import lib.StructureSolver as StructureSolver

import tools.Config as Config

def finder():
    """entry function"""
    path = os.path.join(Config.Path.PROJECT, 'sample', 'kmsg.short')
    fd = open(path, "r")
    sys_log = Parse.Parser(fd)

    #process related
    pTable = PTable.ProcessTable()
    pAdaptor = PAdaptor.ProcessAdaptor(pTable)

    #loaders
    iLoader = ILoader.InterfaceLoader(os.path.join(Config.Path.OUT, Config.System.VERSION, "interface"))
    sSolver = StructureSolver.Solver("Stubs")


    #transaction manger
    tManager = TrManager.TransactionManager(pTable, iLoader, sSolver)

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
    logging.basicConfig(level = logging.DEBUG)
    logger = logging.getLogger(__name__)
    finder()
