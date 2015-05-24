import logging
import plyj.parser as plyj
import JavaLib

logger = logging.getLogger(__name__)

class VariableManager(object):
    def __init__(self):
        globalScope = self.Scope("__global__", "__global__")
        self.vTable = globalScope
        self.path = [globalScope]
        self.pointer = globalScope

    def newScope(self, body):
        unit = body.__class__.__name__
        if  (type(body) == plyj.ClassDeclaration or
        type(body) == plyj.InterfaceDeclaration or
        type(body) == plyj.MethodDeclaration or
        type(body) == plyj.ConstructorDeclaration):
            name = body.name
            logger.debug(">>>>>> {}::{}".format(unit, name))
            localScope = self.Scope(name, unit)
            self.pointer.newVariable(name, localScope)
            self.pointer = localScope
            self.path.append(localScope)

    def leaveScope(self, body):
        unit = body.__class__.__name__
        if  (type(body) == plyj.ClassDeclaration or
        type(body) == plyj.InterfaceDeclaration or
        type(body) == plyj.MethodDeclaration or
        type(body) == plyj.ConstructorDeclaration):
            name = body.name
            logger.debug("<<<<<< {}::{}".format(unit, name))
            del self.path[-1]
            self.pointer = self.path[-1]

    def newVariable(self, name, mtype):
        logger.debug(" {}: \033[1;31m{} \033[0m{}".format(" > ".join(str(i) for i in self.path), mtype, name))
        if  hasattr(self, "includer") and mtype not in JavaLib.builtinMap:
            self.includer.addType(mtype)
        self.pointer.newVariable(name, mtype)

    def setIncluder(self, includer):
        self.includer = includer

    def isExist(self, name):
        pointer = self.vTable
        if  name in pointer:
            return True
        for index in self.path:
            pointer = pointer[index]
            if  name in pointer:
                return True
        return False

    def isMember(self, name):
        preClass = None
        current = self.pointer
        for scope in reversed(self.path):
            if  scope.vtype == "ClassDeclaration":
                preClass = scope
                break
        if  preClass is None:
            return False
        elif  name in current.variables:
            return False
        elif  name in preClass.variables:
            return True
        return False

    def getPath(self):
        return ".".join(str(i) for i in self.path[1:])

    def dump(self):
        return json.dumps(self.vTable, indent=4)

    ##################################################

    class Scope(object):
        """docstring for Scope"""
        def __init__(self, name, vtype):
            self.name = name
            self.vtype = vtype
            self.variables = {}

        def newVariable(self, name, type):
            self.variables[name] = type

        def __str__(self):
            return self.name

        def __repr__(self):
            return str(self.variables)
