"""
Statistic.py

The module is used to count the solving rate of Finder.
At the `end()` function will write the result to the file

"""
import logging
import sys
import os
import json
from collections import defaultdict
import tools.Config as Config

logger = logging.getLogger(__name__)

solvingTable = defaultdict(dict)
total = 0
solved = 0
eTotal = 0
eSolved = 0

SOLVED = "SOLVED"
DISCOVERED = "DISCOVERED"

gDescriptor = None
gCode = None
def solve_start(transaction, descriptor, code):
    global eTotal
    global total
    global solvingTable

    eTotal += 1
    if  descriptor in solvingTable and code in solvingTable[descriptor] and solvingTable[descriptor][code] == SOLVED:
        pass
    elif descriptor in solvingTable and code in solvingTable[descriptor] and solvingTable[descriptor][code] == DISCOVERED:
        pass
    else:
        total += 1
        solvingTable[descriptor][code] = DISCOVERED

    global gDescriptor
    gDescriptor = descriptor
    global gCode
    gCode = code

def solve_success(funcName, *args):
    global eSolved
    global solvingTable
    global solved
    eSolved += 1

    if  solvingTable[gDescriptor][gCode] != SOLVED:
        solved += 1
        solvingTable[gDescriptor][gCode] = SOLVED

def solve_fail():
    print "s fail"

def end():
    if  eTotal != 0 and total != 0:
        out = os.path.abspath(os.path.join(Config.Path.OUT, Config.System.VERSION, "Report"))
        with open(out, "w") as outFd:
            outFd.write("{}\n".format(json.dumps(solvingTable, indent=4, sort_keys=True)))
            outFd.write("\n{}\n=========================\n".format("Solving Rate"))
            outFd.write(" Total: {}\n Solved: {}\n Solving Rate: {}\n".format(eTotal, eSolved, float(eSolved)/float(eTotal) * 100))
            outFd.write("\n{}\n=========================\n".format("coverage"))
            outFd.write(" Total: {}\n Solved: {}\n Solving Rate: {}\n".format(total, solved, float(solved)/float(total) * 100))

def module_init():

    descriptor = {
        "SOLVING_START" : solve_start,
        "SOLVING_SUCCESS" : solve_success,
        "SOLVING_FAIL" : solve_fail,
        "FINDER_END" : end,
    }
    return descriptor
