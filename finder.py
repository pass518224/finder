#! /usr/bin/env python2.7
import logging
import os
import json
import argparse
import sys

import lib.Parse as Parse
import lib.ProcessTable as PTable
import lib.ProcessAdaptor as PAdaptor
import lib.TransactionManager as TrManager
import lib.Transaction as Transaction

import lib.InterfaceLoader as ILoader
import lib.StructureSolver as StructureSolver

import tools.Config as Config

def finder(fd):
    """entry function"""
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

    out = os.path.abspath(os.path.join(Config.Path.OUT, Config.System.VERSION, "Report"))
    with open(out, "w") as outFd:
        outFd.write("{}\n".format(json.dumps(tManager.solvingTable, indent=4, sort_keys=True)))
        outFd.write("\n{}\n=========================\n".format("Solving Rate"))
        outFd.write(" Total: {}\n Solved: {}\n Solving Rate: {}\n".format(tManager.eTotal, tManager.eSolved, float(tManager.eSolved)/float(tManager.eTotal) * 100))
        outFd.write("\n{}\n=========================\n".format("coverage"))
        outFd.write(" Total: {}\n Solved: {}\n Solving Rate: {}\n".format(tManager.total, tManager.solved, float(tManager.solved)/float(tManager.total) * 100))
    #pTable.dumpTable()

if __name__ == '__main__':
    #logging.basicConfig(level = logging.DEBUG)
    logging.basicConfig(level = logging.INFO)
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="finder - Android ICC parser")
    parser.add_argument("input", type=file, nargs="?", help="ICC log file.", default=sys.stdin)
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug trace", default=False)
    args = parser.parse_args()
    Config.DEBUG = args.debug
    
    finder(args.input)
