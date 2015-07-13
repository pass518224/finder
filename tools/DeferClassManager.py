import logging
import json

import Helper

logger = logging.getLogger(__name__)

CLASS = "class"
ANONYMOUS = "anonymous"

class DeferClassManager(object):
    """Manage defered class
        later sort and implement
    """
    def __init__(self, vManager):
        self.vManager = vManager

        #for topological sort
        self.classGraph = {}
        #class container
        self.classes = {}

    def addClass(self, name, dependency, body):
        logger.debug("add CLASS:{} => {}".format(name, dependency))
        self.classGraph[name] = dependency
        self.classes[name] = DeferClass(name, CLASS, body, self.vManager.snapshot())

    def addAnonyClass(self, name, dependency, body):
        logger.debug("add ANONY_CLASS:{} => {}".format(name, dependency))
        self.classGraph[name] = dependency
        self.classes[name] = DeferClass(name, ANONYMOUS, body, self.vManager.snapshot())

    def sort(self):
        result = []
        for className in reversed(Helper.topological(self.classGraph)):
            if  className in self.classes:
                result.append(self.classes[className])
        self.empty()
        return result


    def isEmpty(self):
        return (len(self.classGraph) == 0)

    def empty(self):
        classGraph = self.classGraph
        classes    = self.classes
        self.classGraph = {}
        self.classes    = {}
        return classGraph, classes



class DeferClass(object):
    def __init__(self, name, mtype, obj, VMsnapshot):
        self.name = name
        self.mtype = mtype
        self.obj  = obj
        self.snapshot = VMsnapshot
        
