#!/usr/bin/env python

import logging
import plyj.parser as plyj
import sys
import os
import json
from os import path

import Config
import Selector

logger = logging.getLogger(__name__)

builtinTypes = ["String", "int"]

class Formater(object):
    """docstring for CodeHelper"""
    def __init__(self):
        pass

    def importer(self, file, f = None, a = None):
        if  f:
            f = "from {} ".format(f)
        else:
            f = ""

        if  a:
            a = "as {}".format(a)
        else:
            a = ""
        return "{}import {} {}\n".format(f, file, a)
        
class VariableManager(object):
    def __init__(self):
        self.vTable = {}
        self.path = []
        self.pointer = self.vTable

    def newScope(self, name):
        if name in self.pointer:
            name = name + "I"
        self.pointer[name] = {}
        self.pointer = self.pointer[name]
        self.path.append(name)

    def leaveScope(self):
        del self.path[-1]
        self.pointer = self.vTable
        for node in self.path:
            self.pointer = self.pointer[node]

    def newVariable(self, name, type):
        self.pointer[name] = type

    def update(self, tree):
        self.pointer.update(tree)

    def isExist(self, name):
        pointer = self.vTable
        if  name in pointer:
            return True
        for index in self.path:
            pointer = pointer[index]
            if  name in pointer:
                return True
        return False

    def getLocal(self):
        return self.pointer

    def dump(self):
        return json.dumps(self.vTable, indent=4)

class Compiler(object):
    """docstring for st"""
    # in-class function
    def itemFilter(func):
        """ hook on some function that will generate 'single' name,
        such as : variable name, parameter, hard-code string
        """
        def replaceReservedWord(*args, **kargs):
            _result = func(*args, **kargs)
            reservedWord = {
                    "null"  : "None",
                    "is"    : "_is",
                    "and"   : "_and",
                    "not"   : "_not",
                    "or"    : "_or",
                    "false" : "False",
                    "true"  : "True",
                }
            if  _result in reservedWord:
                _result = reservedWord[_result]
            """docstring for replaceReservedWord"""
            return _result
        return replaceReservedWord

    def __init__(self, fd = None, indent = "    ", level = 0, dependencyPaths = None, vManager = None):
        self.fd = fd
        self.indentPattern = indent
        self.level = level
        self.stopTranslate = False
        self.dependencyPaths = dependencyPaths
        self.hasImplement = False
        self.interfaceCache = {}
        self.imports = {}
        self.siblings = set()
        self.pkgName = ""

        self.formater = Formater()
        if  vManager:
            self.vManager = vManager # function symbol manager
        else:
            self.vManager = VariableManager() # variable symbol manager
        self.dManager = VariableManager() # use to manage dependency of extend/implement variables
        self.managers = []
        self.managers.append(self.vManager)

    def header(self):
        fmtr = self.formater
        self.p( fmtr.importer("Switch", f = "lib.Switch"))
        self.p( fmtr.importer("Stub", f = "lib.Stub"))
        self.p( fmtr.importer("*", f = "lib.JavaUtils"))

    def p(self, fmt):
        if  self.fd is not None:
            self.fd.write(self.indentPattern*(self.level) + fmt)

    def indent(self, name):
        self.level += 1
        for manager in self.managers:
            manager.newScope(name)

    def unindent(self):
        self.level -= 1
        for manager in self.managers:
            manager.leaveScope()

    def compile(self, body):
        """ entry function """
        self.solver(body)
        if  not self.hasImplement:
            raise NotFoundStub

    def crawlDependency(self, name):
        filename = name.split(".")[-1] # get last name seperate by DOT

        if filename in self.vManager.path: # extend/implement from outter scope
            return None

        if  self.dependencyPaths == None: # no given search paths
            return None

        if  filename in self.interfaceCache:
            variableTree = self._index(self.interfaceCache[filename], name)
            self.dManager.update(variableTree)
            return filename

        for searchPath in self.dependencyPaths:
            files = os.listdir(searchPath)
            if  filename + ".java" in files:
                logger.info(name)
                logger.info("Solving interface: [{}]".format(filename))
                parser = plyj.Parser()
                root = parser.parse_file(os.path.join(searchPath, filename + ".java"))
                self.solveInterface(root, filename)
                return filename

    def solveInterface(self, interface, name):
        filename = name.split(".")[-1]
        solvedFile = InterfaceResolver(fd = self.fd)
        solvedFile.compile(interface)
        vTable = solvedFile.vManager.vTable
        self.interfaceCache[filename] = vTable
        variableTree = self._index(vTable, name)
        self.dManager.update(variableTree)

    def _index(self, rootTree, name):
        candidates = []
        for node in rootTree:
            if  node == name:
                return rootTree[node]
            elif type(rootTree[node]) is dict and len(rootTree[node]) > 0:
                candidates.append(node)
        
        for node in candidates:
            result = self._index(rootTree[node], name)
            if  result is not None:
                return result
        return None

    def CompilationUnit(self, body):
        package_declaration = self.solver(body.package_declaration)
        import_declarations = []
        for importer in body.import_declarations:
            import_declarations.append(self.solver(importer))

        type_declarations   = []
        for typer in body.type_declarations:
            type_declarations.append(self.solver(typer))

    def PackageDeclaration(self, body):
        name = self.solver(body.name)
        self.pkgName = name
        for sourcePath in Config.System.JAVA_LIBS:
            pkgPath = path.join(sourcePath, name.replace(".", "/"))
            if  os.path.exists(pkgPath):
                for file in os.listdir(pkgPath):
                    if  file.endswith(".java"):
                        self.siblings.add(file[:-5])
        return 

    def ImportDeclaration(self, body):
        name = self.solver(body.name)
        pkg = name.split(".")[-1]
        self.imports[pkg] = name
        return
        raise Undefined

    def InterfaceDeclaration(self, body):
        name = self.solver(body.name)
        self.solveInterface(body, name)
        #modifiers=<type 'list'>
        #extends=<type 'list'>
        #type_parameters=<type 'list'>
        self.indent(name)
        for comp in body.body:
            self.solver(comp)
        self.unindent()

    def ClassDeclaration(self, body):
        """
        modifiers=<type 'list'>
        type_parameters=<type 'list'>
        extends=<class 'plyj.model.Type'>
        implements=<type 'list'>
        implements = []
        """
        implements = []
        for impl in body.implements:
            interface = self.crawlDependency( self.solver(impl) )
            if  interface is not None:
                implements.append(interface)
        implements.append("Stub")

        name = self.solver(body.name)
        if  name == "Stub" or name.find("Native") > 0:
            self.level = 0
            self.p("class OnTransact({}):\n".format(", ".join(implements)))
            for comp in body.body:
                if  type(comp) == plyj.FieldDeclaration:
                    self.solver(comp)
            self.p("    def onTransact(self, code, data, reply):\n")
            self.vManager.newVariable("reply", "Parcel")
            self.vManager.newVariable("data", "Parcel")
            self.vManager.newVariable("code", "int")
            self.hasImplement = True

        self.indent(name)
        for comp in body.body:
            self.solver(comp)
        self.unindent()

    def FieldDeclaration(self, body):
        mtype = self.solver(body.type)
        variable_declarators = []
        for var in body.variable_declarators:
            if  type(var.initializer) == plyj.Literal:
                variable, initializer = self.solver(var)
                self.p("    {} = {}\n".format(variable, initializer))

    def ConstructorDeclaration(self, body):
        return None

    def MethodDeclaration(self, body):
        name = self.solver(body.name)
        #modifiers=<type 'list'>
        #type_arguments =<type 'list'>
        #parameters=<type 'list'>
        return_type = self.solver(body.return_type)
        #body=<type 'NoneType'>
        #abstract=<type 'bool'>
        #extended_dims=<type 'int'>
        #throws=<class 'plyj.model.Throws'

        if  name == "onTransact" and body is not None:
            self.indent(name)
            for comp in body.body:
                self.solver(comp)
            self.unindent()
        else:
            self.indent(name)
            self.unindent()
        return None
        
    def IfThenElse(self, body):
        predicate = self.solver(body.predicate)
        self.p("if {}:\n".format(predicate))
        self.indent("IF")
        self.solver(body.if_true)
        self.unindent()
        if  body.if_false:
            self.p("else:\n")
            self.indent("ELSE:")
            self.solver(body.if_false)
            self.unindent()
        return None

    def Switch(self, body):

        value = body.expression.value
        cases      = body.switch_cases
        self.p("for mycase in Switch({}):\n".format(value))
        self.indent("Switch")
        for case in cases:
            self.solver(case)
        self.unindent()

    def SwitchCase(self, body):
        cases = body.cases
        body  = body.body

        self.p("if {case}:\n".format(case=" and ".join("mycase(\"" + i.value.split(".")[-1] + "\")" for i in cases)))
        self.indent(" and ".join("mycase(" + i.value + ")" for i in cases))

        for comp in body:
            self.solver(comp)
        self.p("# " + str(self.vManager.getLocal()) + "\n")

        self.unindent()

    def Block(self, body):
        stmts = body.statements
        for stmt in stmts:
            stmt = self.solver(stmt)
            if  stmt:
                self.p((stmt) + "\n")
            if  self.stopTranslate is True:
                self.stopTranslate = False
                return

    def Try(self, body):
        """
        block=<class 'plyj.model.Block'>
        catches=<type 'list'>
        _finally=<type 'NoneType'>
        resources=<type 'list'>
        """
        self.solver(body.block)

    def For(self, body):
        """
        init=<class 'plyj.model.VariableDeclaration'>
        predicate=<class 'plyj.model.Relational'>
        update=<type 'list'>
        body=<class 'plyj.model.Block'>
        """
        self.solver(body.init)
        self.p("while {}:\n".format(self.solver(body.predicate)))
        self.indent("For loop")
        self.solver(body.body)
        for update in body.update:
            self.p(self.solver(update) + "\n")
        self.unindent()

    def Statements(self, body):
        raise Undefined

    def Statement(self, body):
        raise Undefined
    
    def Assignment(self, body):
        # Assignment(operator='=', lhs=Name(value='_arg1'), rhs=MethodInvocation(name='readInt', arguments=[], type_arguments=[], target=Name(value='data')))
        operator = self.solver(body.operator)
        lhs = self.solver(body.lhs)
        rhs = self.solver(body.rhs)
        if  self.stopTranslate:
            return rhs
        return "{lhs} {op} {rhs}".format(lhs = lhs, op = operator, rhs = rhs)


    def Return(self, body):
        return "return {}".format(self.solver(body.result))

    def Type(self, body):
        tArgs = []
        for arg in body.type_arguments:
            tArgs.append(self.solver(arg))
        if  len(tArgs) > 0:
            type_arguments = "<{}>".format(", ".join(tArgs))
        else:
            type_arguments = ""
        enclosed_in=body.enclosed_in
        dimensions=body.dimensions
        name = self.solver(body.name)
        return "{name}{targs}".format(name = name, targs = type_arguments )

    def Conditional(self, body):
        predicate = self.solver(body.predicate)
        if_true = self.solver(body.if_true)
        if_false = self.solver(body.if_false)
        return "{if_true} if {predicate} else {if_false}".format(if_true=if_true, predicate=predicate, if_false = if_false)

    @itemFilter
    def Name(self, body):
        value = body.value
        return value

    @itemFilter
    def Literal(self, body):
        value = body.value
        return value

    @itemFilter
    def Variable(self, body):
        name = body.name
        dimensions = body.dimensions
        return name

    def FormalParameter(self, body):
        """
        variable=<class 'plyj.model.Variable'>
        type=<class 'plyj.model.Type'>
        modifiers=<type 'list'>
        vararg=<type 'bool'>
        """
        variable = self.solver(body.variable)
        mtype = self.solver(body.type)
        self.vManager.newVariable(variable, mtype)

    def InstanceCreation(self, body):
        mtype = self.solver(body.type)
        if  mtype.find("ArrayList") > 0:
            return "list()"
        args = []
        for arg in body.arguments:
            args.append(self.solver(arg))
        return "self.newInstance(\"{}\", {})".format(mtype, ", ".join(i for i in args))

    def VariableDeclaration(self, body):
        mtype = self.solver(body.type)
        variables = []
        for variable in body.variable_declarators:
            variable, initializer = self.solver(variable)
            if  variable:
                self.vManager.newVariable(variable, mtype)
            if  self.stopTranslate:
                variables.append(initializer)
                return "{name}".format(name = ", ".join(i for i in variables))
            if  initializer:
                variables.append("{} = {}".format(variable, initializer))
        modifiers = body.modifiers
        return "{name}".format(name = ", ".join(i for i in variables))

    def VariableDeclarator(self, body):
        variable=self.solver(body.variable)
        initializer=body.initializer
        if  initializer:
            initializer = self.solver(initializer)
            return variable, initializer
        else:
            return variable, None

    def MethodInvocation(self, body):
        name = body.name
        arguments = body.arguments
        args = []
        for arg in arguments:
            _result = self.solver(arg)
            if  self.stopTranslate:
                return _result
            if  _result.find(".CREATOR") > 0:
                offset = _result.find(".CREATOR")
                _result = _result[:offset]
                args.append("\"{}\"".format(_result))
                """
                if  len( _result.split(".") ) <= 1:
                    raise Exception(_result)
                """
                creators.add(_result)
            else:
                args.append(_result)

        type_arguments = body.type_arguments
        if  self.dManager.isExist(name):
            target = "self"
            args.insert(0, "\"{}\"".format(name))
            self.stopTranslate = True
            return "return {target}.callFunction({args})".format(target = target, args = ", ".join(i for i in args))

        if body.target is None:
            if  name in exitFunctions:
                args.insert(0, "\"{}\"".format(name))
                self.stopTranslate = True
                return "return self.callFunction({})".format(", ".join(i for i in args))
            else:
                return "{name}({args})".format(name = name, args = ", ".join(i for i in args))
        target = self.solver(body.target)

        if target == "super":
            return None
        elif body.target == "this": # call interface function
            target = "self"
            args.insert(0, "\"{}\"".format(name))
            self.stopTranslate = True
            return "return {target}.callFunction({args})".format(target = target, args = ", ".join(i for i in args))

        if  name == "createFromParcel":
            offset = target.find(".CREATOR")
            target = target[:offset]
            if  target in self.imports:
                target = self.imports[target]
            elif target in self.siblings:
                target = "{}.{}".format(self.pkgName, target)
            args.insert(0, "\"{}\"".format(target))
            """
            if  len( target.split(".") ) <= 1:
                raise Exception(target)
            """
            creators.add(target)
            return "self.creatorResolver({args})".format(args = ", ".join(i for i in args))

        if  name == "asInterface":
            offset = target.find(".Stub")
            target = target[:offset]
            args.insert(0, "\"" + target + "\"")
            return "self.interfaceResolver({args})".format(args = ", ".join(i for i in args))

        if not self.vManager.isExist(target):
            return "\'{target}.{name}({args})\'".format(target = target, name = name, args = ", ".join(i for i in args))

        return "{target}.{name}({args})".format(target = target, name = name, args = ", ".join(i for i in args))
    
    def Equality(self, body):
        operator = self.solver(body.operator)
        lhs = self.solver(body.lhs)
        rhs = self.solver(body.rhs)
        return "({} {} {})".format(lhs, operator, rhs)

    def Relational(self, body):
        operator = self.solver(body.operator)
        lhs = self.solver(body.lhs)
        rhs = self.solver(body.rhs)
        return "({} {} {})".format(lhs, operator, rhs)

    def Additive(self, body):
        operator = self.solver(body.operator)
        lhs = self.solver(body.lhs)
        rhs = self.solver(body.rhs)
        return "({} {} {})".format(lhs, operator, rhs)
    
    def Unary(self, body):
        """
        sign=<type 'str'>
        expression=<class 'plyj.model.Literal'>
        """
        sign = body.sign
        expression = self.solver(body.expression)
        if  sign == "x++":
            return "{} += 1".format(expression)
        return "{}{}".format(sign, expression)

    def Cast(self, body):
        return

    def ArrayCreation(self, body):
        # ArrayCreation(type='int', dimensions=[Name(value='_arg4_length')], initializer=None)
        mtype = self.solver(body.type)
        if  mtype in builtinTypes:
            mtype = ""
        dims = []
        for dim in body.dimensions:
            dims.append(self.solver(dim))
        dimensions = "".join("[None for _i in range({})]".format(i) for i in dims)
        initializer = body.initializer
        return "{dimensions} # {type}".format(type = mtype, dimensions = dimensions)
    
    def ArrayAccess(self, body):
        """
        index=<class 'plyj.model.Name'>
        target=<class 'plyj.model.Name'>
        """
        index = self.solver(body.index)
        target = self.solver(body.target)
        return "{}[{}]".format(target, index)

    def solver(self, thing):
        if  type(thing) == type(None):
            return thing
        if  type(thing) == str:
            return thing
        return getattr(self, thing.__class__.__name__)(thing)



class InterfaceResolver(Compiler):
    """docstring for InterfaceResolver"""
    def __init__(self, *args, **kargs):
        super(InterfaceResolver, self).__init__(*args, **kargs)

    def InterfaceDeclaration(self, body):
        name = self.solver(body.name)
        #modifiers=<type 'list'>
        #extends=<type 'list'>
        #type_parameters=<type 'list'>
        self.p("class {}:\n".format(name))
        self.p("    pass\n")
        self.indent(name)
        for comp in body.body:
            self.solver(comp)
        self.unindent()
        
    def ClassDeclaration(self, body):
        return

    def FieldDeclaration(self, body):
        mtype = self.solver(body.type)
        variable_declarators = []
        for var in body.variable_declarators:
            if  type(var.initializer) == plyj.Literal:
                variable, initializer = self.solver(var)
                self.p("{} = {}\n".format(variable, initializer))

    def MethodDeclaration(self, body):
        name = self.solver(body.name)
        return_type = self.solver(body.return_type)

        self.indent(name)
        self.unindent()
        return None

    def crawlDependency(self, name):
        return 

    def compile(self, body):
        """ entry function """
        self.solver(body)
        
         
class Undefined(Exception):
    pass

class NotFoundStub(Exception):
    pass

def dumper(body):
    if hasattr(body, "_fields"):
        for attr in body._fields:
            print "{}={}".format(attr, type(getattr(body, attr)))
    else:
        print body

    """docstring for dumper"""
    pass

def translator(inputFd, outputFd):
    """ translate AIDL-generated java file into python file"""
    parser = plyj.Parser()

    root = parser.parse_file(inputFd)

    #compiler = Compiler(outputFd)
    search = os.path.join(Config.Path._IINTERFACE, Config.System.VERSION)
    compiler = Compiler(fd = outputFd, dependencyPaths = [search])
    compiler.header()
    compiler.compile(root)


if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    creators = set()

    
    """
    exitFunctions = set()
    inputPath = os.path.join( Config.Path._NATIVE_STUB, Config.System.VERSION, "ActivityManagerNative.java")
    nativeMethodPath = "ClassDeclaration[name$=Proxy]>MethodDeclaration[throws*=RemoteException]"
    result = Selector.Selector(inputPath).query(nativeMethodPath)
    for item in result:
        exitFunctions.add(item.name)
    with open(inputPath, "r") as inputFd:
        translator(inputFd, sys.stdout)
    """

    sourcePath = os.path.join( Config.Path._IINTERFACE, Config.System.VERSION)
    outputPath = os.path.join(Config.Path.OUT, Config.System.VERSION, "stub")
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    for file in os.listdir(sourcePath):
        inputFile = os.path.join(sourcePath, file)
        exitFunctions = set()
        outputFile = os.path.join(outputPath, ".".join(file.split(".")[:-1])+".py")
        with open(inputFile, "r") as inputFd, open(outputFile, "w") as outputFd:
            logger.info("parsing file: [{}]".format(file))
            try:
                translator(inputFd, outputFd)
            except NotFoundStub as e:
                os.remove(outputFile)
                logger.warn("Not Found stub in file. # remove '{}'".format(file))

    sourcePath = os.path.join(Config.Path._NATIVE_STUB, Config.System.VERSION)
    for file in os.listdir(sourcePath):
        inputFile = os.path.join(sourcePath, file)
        exitFunctions = set()
        nativeMethodPath = "ClassDeclaration[name$=Proxy]>MethodDeclaration[throws*=RemoteException]"
        result = Selector.Selector(inputFile).query(nativeMethodPath)
        for item in result:
            exitFunctions.add(item.name)
        outputFile = os.path.join(outputPath, ".".join(file.split(".")[:-1])+".py")
        with open(inputFile, "r") as inputFd, open(outputFile, "w") as outputFd:
            logger.info("parsing file: [{}]".format(file))
            try:
                translator(inputFd, outputFd)
            except NotFoundStub as e:
                os.remove(outputFile)
                logger.warn("Not Found stub in file. # remove '{}'".format(file))

    parcelList = path.join( Config.Path.OUT, Config.System.VERSION, "Parcel_list")
    with open(parcelList, "w") as pfd:
        pfd.write("\n".join(creators))
