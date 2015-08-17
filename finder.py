#!/usr/bin/env python2.7 -W ignore
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
import lib.Module as Module
from lib.FilterAdaptor import FilterAdaptor

import tools.Config as Config

def finder(fd, filter=None, ps=None):
    """finder entry function"""
    sys_log = Parse.Parser(fd)

    #process related
    pTable = PTable.ProcessTable()
    if  ps:
        pTable.readFromPs(ps)
    pAdaptor = PAdaptor.ProcessAdaptor(pTable)

    #loaders
    iLoader = ILoader.InterfaceLoader(os.path.join(Config.Path.OUT, Config.System.VERSION, "interface"))
    sSolver = StructureSolver.Solver("Stubs")


    #transaction manger
    tManager = TrManager.TransactionManager(pTable, iLoader, sSolver)
    if  filter:
        tManager.registFilter(filter)

    #finder start hook point
    Module.getModule().call("FINDER_START")

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
                tra =  Transaction.Transaction(sys_log.getInfo()) 
                tManager.addTransaction(tra)
                tManager.solve(tra)
            except Transaction.TransactionError as e:
                logger.warn("transaction error: " + e.args[0])
    #tManager.list()
    logger.info(tManager.getMissedTransaction())

    #finder end hook point
    Module.getModule().call("FINDER_END")

def parseArgument():
    parser = argparse.ArgumentParser(description="finder - Android ICC parser")
    parser.add_argument("input", type=file, nargs="?", help="ICC log file.", default=sys.stdin)
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug trace", default=False)

    #contain filter options
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--sender", help="only show filter from the pattern")
    group.add_argument("-r", "--receiver", help="only show filter to the pattern")
    group.add_argument("-c", "--contain", help="only show filter contained the pattern")

    parser.add_argument("-n", "--negation", action="store_true", help="negate the result of filter", default=False)
    parser.add_argument("--black-list", type=file, metavar="FILEPATH", help="Block the ICC transaction in blacklist")

    #show log info
    parser.add_argument("--info", action="store_true", help="show log info", default=False)

    parser.add_argument("--not-solve", action="store_true", help="not to solve ICC data", default=False)

    #ps file to complete process name
    parser.add_argument("--ps", metavar="CHROME.PS", type=file, help="ps cmd result")

    args = parser.parse_args()

    Config.DEBUG = args.debug
    Config.NOT_SOLVE = args.not_solve
    return args

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    logger = logging.getLogger(__name__)

    args = parseArgument()
    filter = FilterAdaptor(args).getFilter()
    
    Module.getModule().add("Statistic")
    Module.getModule().add("TimeSlicer")
    
    finder(args.input, filter=filter, ps=args.ps)
