#!/usr/bin/env python

import logging
import plyj.parser as plyj
import sys
import os
import json

import Config

logger = logging.getLogger(__name__)

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

    def isExist(self, name):
        for level in self.vTable:
            if  name in level:
                return True
        return False

    def getLocal(self):
        return self.pointer

    def dump(self):
        print json.dumps(self.vTable, sort_keys=True, indent=4)

class Compiler(object):
    """docstring for st"""
    def __init__(self, fd = None, indent = "    ", level = 0, dependencyPath = None, vManager = None):
        self.fd = fd
        self.indentPattern = indent
        self.level = level
        self.stopTranslate = False
        self.dependencyPath = dependencyPath

        self.formater = Formater()
        if  vManager:
            self.vManager = vManager # function symbol manager
        else:
            self.vManager = VariableManager() # variable symbol manager
        self.managers = []
        self.managers.append(self.vManager)

    def initializer(self):
        fmtr = self.formater
        self.p( fmtr.importer("Switch", f = "Switch"))
        self.p( fmtr.importer("Stub", f = "Stub"))
        self.p("class OnTransact(Stub):\n")
        self.level += 1
        self.p("def __init__(self, code, data)\n")
        self.level += 1

    def p(self, fmt):
        if  self.fd is not None:
            self.fd.write(self.indentPattern*self.level + fmt)

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

    def CompilationUnit(self, body):
        package_declaration = self.solver(body.package_declaration)
        import_declarations = []
        for importer in body.import_declarations:
            import_declarations.append(self.solver(importer))

        type_declarations   = []
        for typer in body.type_declarations:
            type_declarations.append(self.solver(typer))

    def PackageDeclaration(self, body):
        return self.solver(body.name)

    def ImportDeclaration(self, body):
        return
        raise Undefined

    def InterfaceDeclaration(self, body):
        name = self.solver(body.name)
        #modifiers=<type 'list'>
        #extends=<type 'list'>
        #type_parameters=<type 'list'>
        for comp in body.body:
            self.solver(comp)

    def ClassDeclaration(self, body):
        """
        modifiers=<type 'list'>
        type_parameters=<type 'list'>
        extends=<class 'plyj.model.Type'>
        implements=<type 'list'>
        implements = []
        for impl in body.implements:
            implements.append( self.solver.impl)
        """
        name = self.solver(body.name)
        self.indent(name)
        if  name == "Stub" or name.find("Native") > 0:
            for comp in body.body:
                self.solver(comp)
        self.unindent()

    def FieldDeclaration(self, body):
        mtype = self.solver(body.type)
        variable_declarators = []
        for var in body.variable_declarators:
            variable_declarators.append( self.solver(var))
        #modifiers=<type 'list'>

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

        self.indent(name)
        if  name == "onTransact" and body is not None:
            for comp in body.body:
                self.solver(comp)
            self.unindent()
        else:
            self.unindent()
            return None
        
    def IfThenElse(self, body):
        predicate = self.solver(body.predicate)
        self.p("if ({}):\n".format(predicate))
        self.indent("IF")
        self.solver(body.if_true)
        self.unindent()
        self.p("else:\n".format(predicate))
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
            getattr(self, case.__class__.__name__)(case)
        self.unindent()

    def SwitchCase(self, body):
        cases = body.cases
        body  = body.body

        self.p("if {case}:\n".format(case=" and ".join("mycase(" + i.value + ")" for i in cases)))
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

    def Statements(self, body):
        raise Undefined

    def Statement(self, body):
        raise Undefined
    
    def Assignment(self, body):
        # Assignment(operator='=', lhs=Name(value='_arg1'), rhs=MethodInvocation(name='readInt', arguments=[], type_arguments=[], target=Name(value='data')))
        operator = self.solver(body.operator)
        lhs = self.solver(body.lhs)
        rhs = self.solver(body.rhs)
        return "{lhs} {op} {rhs}".format(lhs = lhs, op = operator, rhs = rhs)


    def Return(self, body):
        return "return {}".format(self.solver(body.result))

    def Name(self, body):
        if  type(body) is str:
            return body
        return body.value

    def Type(self, body):
        if  type(body) is str:
            return body
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
        predicate = getattr(self, body.predicate.__class__.__name__)(body.predicate)
        if_true = getattr(self, body.if_true.__class__.__name__)(body.if_true)
        if_false = getattr(self, body.if_false.__class__.__name__)(body.if_false)
        return "{if_true} if {predicate} else {if_false}".format(if_true=if_true, predicate=predicate, if_false = if_false)

    def Literal(self, body):
        return body.value

    def Variable(self, body):
        name = body.name
        dimensions = body.dimensions
        return body.name

    def InstanceCreation(self, body):
        """
        InstanceCreation(
        type=Type(name=Name(value='java.util.ArrayList'), type_arguments=[Type(name=Name(value='android.widget.RemoteViews'), type_arguments=[], enclosed_in=None, dimensions=0)], enclosed_in=None, dimensions=0),
        type_arguments=[],
        arguments=[],
        body=[],
        enclosed_in=None)
        """
        mtype = self.solver(body.type)
        args = []
        for arg in body.arguments:
            args.append(self.solver(arg))
        return "{}({})".format(mtype, ", ".join(i for i in args))

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
            fun = getattr(self, arg.__class__.__name__)
            args.append(fun(arg))
        type_arguments = body.type_arguments
        if body.target is None:
            return "{name}({args})".format(name = name, args = ", ".join(i for i in args))

        target = self.solver(body.target)
        if  target == "reply":
            return None
        elif target == "super":
            return None
        elif body.target == "this": # call interface function
            target = "self"
            args.insert(0, "\"{}\"".format(name))
            self.stopTranslate = True
            return "return {target}.callFunction({args})".format(target = target, args = ", ".join(i for i in args))

        if  name == "createFromParcel":
            offset = target.find(".CREATOR")
            target = target[:offset]
            args.insert(0, "\"{}\"".format(target))
            creators.add(target)
            return "self.creatorResolver({args})".format(args = ", ".join(i for i in args))

        if  name == "asInterface":
            offset = target.find(".Stub")
            target = target[:offset]
            args.insert(0, target)
            return "self.interfaceResolver({args})".format(args = ", ".join(i for i in args))

        if  not self.vManager.isExist(target):
            logger.warn("{target}.{name}({args})".format(target = target, name = name, args = ", ".join(i for i in args)))
        
        return "{target}.{name}({args})".format(target = target, name = name, args = ", ".join(i for i in args))
    
    def Equality(self, body):
        operator = self.solver(body.operator)
        lhs = self.solver(body.lhs)
        rhs = self.solver(body.rhs)
        return "{} {} {}".format(lhs, operator, rhs)

    def Relational(self, body):
        operator = self.solver(body.operator)
        lhs = self.solver(body.lhs)
        rhs = self.solver(body.rhs)
        return "{} {} {}".format(lhs, operator, rhs)

    def Additive(self, body):
        operator = self.solver(body.operator)
        lhs = self.solver(body.lhs)
        rhs = self.solver(body.rhs)
        return "{} {} {}".format(lhs, operator, rhs)
    
    def Unary(self, body):
        """
        sign=<type 'str'>
        expression=<class 'plyj.model.Literal'>
        """
        sign = body.sign
        expression = self.solver(body.expression)
        return "{}{}".format(sign, expression)

    def ArrayCreation(self, body):
        # ArrayCreation(type='int', dimensions=[Name(value='_arg4_length')], initializer=None)
        mtype = self.solver(body.type)
        dims = []
        for dim in body.dimensions:
            dims.append(self.solver(dim))
        dimensions = "".join("[{}]".format(i) for i in dims)
        initializer = body.initializer
        return "{type}{dimensions}".format(type = mtype, dimensions = dimensions)

    def parse_body(self, body):
        for comp in body:
            name = comp.__class__.__name__
            fun = getattr(self, name)
            fun(comp)

    def solver(self, thing):
        if  type(thing) == type(None):
            return thing
        if  type(thing) == str:
            return thing
        logger.debug(self.indentPattern*self.level + thing.__class__.__name__)
        return getattr(self, thing.__class__.__name__)(thing)

class InterfaceResolver(Compiler):
    """docstring for InterfaceResolver"""
    def __init__(self, *args, **kargs):
        kargs["vManager"] = Manager()
        super(InterfaceResolver, self).__init__(*args, **kargs)

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

    class Manager(VariableManager):
        def unindent(self):
            pass
            
        
         
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
    compiler = Compiler()
    compiler.initializer()
    compiler.compile(root)
    compiler.vManager.dump()
    """
    body = root.type_declarations[0].body

    # search class 'Stub'
    classStub = None
    for comp in body:
        if  hasattr(comp, "name"):
            if  comp.name == "Stub":
                classStub = comp
                break

    #not found class Stub
    if classStub is None:
        raise NotFoundStub

    for method in classStub.body:
        if  type(method) == plyj.MethodDeclaration and method.name == "onTransact":
            methodTransact = method
            break

    compiler = Compiler(outputFd)
    compiler = Compiler()
    compiler.initializer()
    compiler.parse_body(methodTransact.body)
    """


if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.WARN)
    creators = set()

    
    inputPath = "/home/lucas/WORKING_DIRECTORY/kernel/goldfish/Finder/_IInterface/IBluetooth.java"
    #inputPath = "/home/lucas/WORKING_DIRECTORY/kernel/goldfish/Finder/_IInterface/IActivityManager.java"


    with open(inputPath, "r") as inputFd:
        translator(inputFd, sys.stdout)

    """
    sourcePath = Config.Path._IINTERFACE
    outputPath = Config.Path.OUT

    for file in os.listdir(sourcePath):
        with open(os.path.join(sourcePath, file), "r") as inputFd, open(os.path.join(outputPath, "Stub", ".".join(file.split(".")[:-1])+".py"), "w") as outputFd:
            logger.info(file)
            try:
                translator(inputFd, outputFd)
            except NotFoundStub as e:
                print file
    print creators
    """
