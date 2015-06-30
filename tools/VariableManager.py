import logging
import plyj.parser as plyj
import JavaLib
import json

import IAdaptor
import Helper

logger = logging.getLogger(__name__)

CALLABLE = "callable"
VARIABLE = "variable"

class VariableManager(object):
    def __init__(self):
        self.iAdaptor = IAdaptor.IncludeAdaptor()
        globalScope = self.Scope("__global__", "__global__")
        self.vTable = globalScope
        self.path = [globalScope]
        self.current = globalScope
        self.classPaths = {}
        self.reversedClassPaths = {}

        #member tabel
        self.members = {}
        self.reversedMember = {}

    def snapshot(self):
        path = list(self.path)
        current = self.current
        return (path, current)

    def setSnapshot(self, snapshot):
        path, current = snapshot
        self.path = path
        self.current = current


    def setIAdaptor(self, iAdaptor):
        self.iAdaptor = iAdaptor


    def newScope(self, body):
        unit = body.__class__.__name__
        if  type(body) in [plyj.ClassDeclaration, plyj.InterfaceDeclaration, plyj.MethodDeclaration, plyj.ConstructorDeclaration]:
            name = Helper.keywordReplace_helper(body.name)
            logger.debug(">>>>>> {}::{}".format(unit, name))
            localScope = self.current.getCallableVariable(name)
            if  not localScope:
                localScope = self.Scope(name, unit)
                localScope.update(self.current)
            self.current.newCallable(name, localScope)
            self.current = localScope
            self.path.append(localScope)

            if  type(body) == plyj.ClassDeclaration or type(body) == plyj.InterfaceDeclaration:
                if  name not in self.classPaths:
                    self.classPaths[name] = self.getPath()
                    self.reversedClassPaths[self.getPath()] = name

    def getPath(self):
        return ".".join(i.name for i in self.path[1:])

    def leaveScope(self, body):
        unit = body.__class__.__name__
        if  (type(body) == plyj.ClassDeclaration or
        type(body) == plyj.InterfaceDeclaration or
        type(body) == plyj.MethodDeclaration or
        type(body) == plyj.ConstructorDeclaration):
            name = body.name
            logger.debug("<<<<<< {}::{}".format(unit, name))
            del self.path[-1]
            self.current = self.path[-1]

    def addMacro(self, name):
        globalPath = self.getPath() + "." + name
        self.current.addMacro(name, globalPath)

    def addInherit(self, cls):
        if not self.findClass(cls):
            self.iAdaptor.addInherit(cls)

    def newVariable(self, name, mtype, isMember=False):
        logger.debug(" {}: \033[1;31m{} \033[0m{}".format(" > ".join(str(i) for i in self.path), mtype, name))
        self.current.newVariable(name, mtype)
        if  isMember and name not in self.members:
            self.members[name] = self.getPath() + "." + name
            self.reversedMember[self.getPath() + "." + name] = name

    def getType(self, vname):
        """return variable type"""
        if  vname not in self.current.variables:
            raise Exception("None exist variables: {}".format(vname))
        return self.current.variables[vname]

    def isMember(self, name):
        preClass = None
        for scope in reversed(self.path):
            if  scope.vtype == "ClassDeclaration":
                preClass = scope
                break
        if  preClass is None:
            return False
        elif  self.current.isDeclared(name):
            return False
        elif  preClass.isDeclared(name):
            return True
        return False

    def decorate(self, variable, SELF_INSTANCE):
        """ decorate variable to fix its position, such as: ^self. , absolute member"""
        if  self.isMember(variable):
            return "{}.{}".format(SELF_INSTANCE, variable)
        if  variable in self.current.globalAddress:
            return self.current.globalAddress[variable]
        return variable

    def findClass(self, clsName):
        if  clsName in self.classPaths:
            return self.classPaths[clsName]
        return None

    def getFullPathByName(self, cls):
        if  cls not in self.classPaths:
            raise Exception("Try to access a none self class: {}".format(cls))
        return self.classPaths[cls]

    def getPath(self):
        return ".".join(str(i) for i in self.path[1:])

    def dump(self):
        return self._dump(self.vTable)

    def _dump(self, scope, level=0, pattern="    "):
        result = ""
        indent = pattern * level
        level += 1
        for k, v in scope.variables.items():
            result += "{}{}:{}\n".format(indent, k, v)

        for k, v in scope.callables.items():
            result += "{}{}:[\n".format(indent, k)
            result += self._dump(v, level)
            result += "{}]\n".format(indent)
        return result
    
    def status(self):
        result  = "========================================\n"
        result += "Path: {}\n".format(self.getPath())
        result += "callables: \n{}\n".format(json.dumps([i for i in self.current.callables], indent=4))
        result += "variables: \n{}\n".format(json.dumps(self.current.variables, indent=4))
        result += "globalAddress: \n{}\n".format(json.dumps(self.current.globalAddress, indent=4))
        result += "========================================\n"
        return result

    ##################################################

    class Scope(object):
        """docstring for Scope"""
        def __init__(self, name, vtype):
            self.name = name
            self.vtype = vtype
            self.globalAddress = {}
            self.variables = {}
            self.callables = {}

            if  vtype == "ClassDeclaration":
                self.variables["__class__"] = "dict"

        def isDeclared(self, name, type=None):
            if  type == CALLABLE and name in self.callables:
                return True
            elif type == VARIABLE and name in self.variables:
                return True
            elif  name in self.variables or name in self.callables:
                return True
            return False

        def newCallable(self, name, type):
            self.callables[name] = type

        def newVariable(self, name, type):
            self.variables[name] = type

        def addMacro(self, name, address):
            self.globalAddress[name] = address

        def update(self, scope):
            self.globalAddress = dict(scope.globalAddress)

        def getCallableVariable(self, name):
            if  name in self.callables:
                return self.callables[name]
            else:
                return None

        def __str__(self):
            return self.name

        def __repr__(self):
            return str(self.variables)

class NeedFixName(Exception):
    pass

