#! /usr/bin/env python2.7
import logging

import lib.Parse as Parse
import lib.ProcessTable as PTable
import lib.ProcessAdaptor as PAdaptor

def finder():
    """entry function"""
    fd = open("/home/lucas/Downloads/syslog/kmsg.sample", "r")
    sys_log = Parse.Parser(fd)
    pTable = PTable.ProcessTable()
    pAdaptor = PAdaptor.ProcessAdaptor(pTable)
    for flag in sys_log:
        if flag == Parse.INFO:
            # handle system INFO
            info = sys_log.getInfo()
            try:
                pAdaptor.action(info)
            except PAdaptor.UnknownRule:
                logging.warn("unknown rule: " + str(info))

    #pTable.dumpTable()

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    logger = logging.getLogger(__name__)
    finder()
