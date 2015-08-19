"""
TimeSlicer.py

This module statistic the total amount of type of ICC with time quantum.
The config of this module is at `TimeSlicer.ini`.

The `config` field is the main config of this module, such as time quantum.

The other name except of config is taken as class of types.
The following name are the corresponding rescriptor and code name.
"""
import logging
import ConfigParser
import datetime
import operator
from collections import defaultdict
from collections import OrderedDict

import tools.Config as Config

logger = logging.getLogger(__name__)

class Session(object):
    """docstring for ClassName"""
    def __init__(self, quantum):
        self.quantum = quantum
        self.preTime = 0
        self.countTable = defaultdict(int)
        self.store = OrderedDict()
        self.total = defaultdict(int)

    def sum(self, role, add):
        for key, val in add.iteritems():
            role[key] += val

    def newSession(self, ctime):
        self.sum(self.total, self.countTable)
        self.store[self.preTime] = self.countTable
        self.countTable = defaultdict(int)
        self.preTime = self.preTime + self.quantum

    def p(self):
        counter = 0
        serialNumber = {}
        table = []
        length = len(self.total)
        for desceiptor in self.total:
            serialNumber[desceiptor] = counter
            counter += 1

        for time, session in self.store.iteritems():
            raw = [0] * length
            for desceiptor, times in session.iteritems():
                offset = serialNumber[desceiptor]
                raw[offset] = times
            raw.insert(0, time)
            table.append(raw)
        print "0," + ",".join(i[0] for i in sorted(serialNumber.items(), key=operator.itemgetter(1)))
        for raw in table:
            print ",".join(str(i) for i in raw)

    def add(self, tra, descriptor, code):
        global gRevTypeTable
        tra.time = int(tra.time)
        
        if  self.preTime == 0:
            self.preTime = tra.time
        elif self.preTime + self.quantum < tra.time:
            self.newSession(tra.time)

        if  descriptor in gRevTypeTable:
            name = gRevTypeTable[descriptor]
        else:
            name = descriptor
        self.countTable[name] += 1

gSession = None
        

gConfig = {}
gSections = set()
gTypeTable = defaultdict(set)
gRevTypeTable = {}

def load(parser):
    global gTypeTable, gRevTypeTable, gSections

    for section in parser.sections():
        gSections.add(section)
        for descriptor, value in parser.items(section):
            gTypeTable[section].add(descriptor)
            gRevTypeTable[descriptor] = section

def start():
    global gConfig
    global gSession 
    parser = ConfigParser.RawConfigParser(allow_no_value=True)
    parser.optionxform = str
    parser.read(Config.absjoin(Config.Path.MODULE, "TimeSlicer.ini" ))
    for key, val in parser.items("config"):
        gConfig[key] = val

    load(parser)
    gSession = Session(int(gConfig["time_quantum"]))

def solving_start(transaction, descriptor, code):
    global gSession
    gSession.add(transaction, descriptor, code)

def end():
    global gSession
    gSession.p()

def module_init():
    descriptor = {
            "FINDER_START": start,
            "SOLVING_START": solving_start,
            "FINDER_END": end,
            }
    return descriptor
