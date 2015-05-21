#!/usr/bin/env python

import logging
import plyj.parser as plyj
import sys
import os
import json
import random
import string
import inspect

from VariableManager import VariableManager

import Config

logger = logging.getLogger(__name__)

class Compiler(object):
    """Java to Python compiler"""
    def __init__(self, fd = None, indent = "    ", dependencyPaths = None, vManager = None):
        logger.debug("Create compiler with args: fd:{}, indent:<{}>, dependencyPaths: {}>, vManager:{}".format(
            "Yes" if fd else "No", indent, dependencyPaths, "Yes" if vManager else " No"
            ))
        self.fd = fd
        self.indentPattern = indent
        self.level = 0
        self.stopTranslate = False
        self.dependencyPaths = dependencyPaths
        self.interfaceCache = {}

        if  vManager:
            self.vManager = vManager # function symbol manager
        else:
            self.vManager = VariableManager() # variable symbol manager
        self.dManager = VariableManager() # use to manage dependency of extend/implement variables
        self.managers = []
        self.managers.append(self.vManager)

    """ decorators """
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
                    "String"  : "str",
                    "Integer"  : "int",
                }
            if  _result in reservedWord:
                _result = reservedWord[_result]
            """docstring for replaceReservedWord"""
            return _result
        return replaceReservedWord


    # Compiler Utilitie
    def c(self, fmt):
        if  self.fd is not None:
            self.fd.write("\n{}# {}\n".format(self.indentPattern*(self.level), fmt))

    def p(self, fmt):
        if  self.fd is not None:
            self.fd.write(self.indentPattern*(self.level) + fmt)

    def indent(self, body, **kargs):
        self.level += 1
        for manager in self.managers:
            manager.newScope(body, **kargs)

    def unindent(self, body, **kargs):
        self.level -= 1
        for manager in self.managers:
            manager.leaveScope(body, **kargs)

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
        self.c("package " + self.solver(body.name))

    def ImportDeclaration(self, body):
        self.c("import {}".format(self.solver(body.name)))

    def InterfaceDeclaration(self, body):
        name = self.solver(body.name)
        self.solveInterface(body, name)
        self.indent(body)
        for comp in body.body:
            self.solver(comp)
        self.unindent(body)

    def ClassDeclaration(self, body):
        """
        extends=<class 'plyj.model.Type'>
        implements=<type 'list'>
        """
        implements = []
        if  body.extends:
            implements.append(self.solver(body.extends))
        for impl in body.implements:
            implements.append(self.solver(impl))

        name = self.solver(body.name)

        self.p("class {name}({parent}):\n".format(name = name, parent = ", ".join(implements)))

        self.indent(body)
        #field process
        for comp in body.body:
            if  type(comp) == plyj.FieldDeclaration:
                self.solver(comp)
                body.body.remove(comp)
        #body preprocess
        function_methods = set()
        overloading = []
        for comp in body.body:
            if  type(comp) == plyj.MethodDeclaration or type(comp) == plyj.ConstructorDeclaration:
                functionName = self.solver(comp.name)
                overloading.append(functionName) if functionName in function_methods else function_methods.add(functionName)

        if  len(overloading) > 0:
            temp = set(overloading)
            if  name in temp:
                temp.remove(name)
                temp.add("__init__")
            self.overloadEntry(temp)
        for comp in body.body:
            if  type(comp) == plyj.MethodDeclaration or type(comp) == plyj.ConstructorDeclaration:
                functionName = self.solver(comp.name)
                if  functionName in overloading:
                    self.solver(comp, appendName=True)
                else:
                    self.solver(comp)
            else:
                self.solver(comp)
        self.unindent(body)

    def FieldDeclaration(self, body):
        mtype = self.solver(body.type)
        variable_declarators = []
        for var in body.variable_declarators:
            variable, initializer = self.solver(var)
            self.vManager.newVariable(variable, mtype)
            if  initializer is None:
                self.c(mtype)
                self.p("{} = None\n".format(variable))
                continue
            self.p("{} = {}\n".format(variable, initializer))


    def ConstructorDeclaration(self, body, appendName = False):
        """
        name=<type 'str'>
        block=<type 'list'>
        type_parameters=<type 'list'>
        parameters=<type 'list'>
        """
        setattr(body, "body", body.block)
        self._classMethodDeclaration(body, appendName, functionName="__init__")

    def MethodDeclaration(self, body, appendName = False):
        """
        name=<type 'str'>
        type_parameters=<type 'list'>
        parameters=<type 'list'>
        return_type=<type 'str'>
        body=<type 'list'>
        abstract=<type 'bool'>
        """
        self._classMethodDeclaration(body, appendName)
    
    def _classMethodDeclaration(self, body, appendName = False, functionName = None):
        args = ["self"]
        args_type = []
        self.indent(body)
        for arg in body.parameters:
            name, mtype = self.solver(arg)
            args.append(name)
            args_type.append(mtype)

        if  not functionName:
            functionName = self.solver(body.name)

        self.level -= 1
        self.p("def {}{}{}({}):\n".format(functionName,
            "__" if appendName else "",
            "_______".join(args_type) if appendName else "",
            ", ".join(args)))
        self.level += 1

        if  len(body.body) == 0:
            self.p("pass\n")
        for stmt in body.body:
            result = self.solver(stmt)
            if  result:
                self.p(result + "\n")
        self.unindent(body)
        
    def IfThenElse(self, body):
        predicate = self.solver(body.predicate)
        self.p("if {}:\n".format(predicate))
        self.indent(body)
        self.solver(body.if_true)
        self.unindent(body)
        if  body.if_false:
            self.p("else:\n")
            self.indent(body)
            self.solver(body.if_false)
            self.unindent(body)
        return None

    def Switch(self, body):

        value = body.expression.value
        cases      = body.switch_cases
        self.p("for mycase in Switch({}):\n".format(value))
        self.indent(body)
        for case in cases:
            self.solver(case)
        self.unindent(body)

    def SwitchCase(self, body):
        cases = body.cases
        body  = body.body

        self.p("if {case}:\n".format(case=" and ".join("mycase(\"" + i.value.split(".")[-1] + "\")" for i in cases)))
        self.indent(body)

        for comp in body:
            self.solver(comp)

        self.unindent(body)

    def Block(self, body):
        stmts = body.statements
        for stmt in stmts:
            stmt = self.solver(stmt)
            if  stmt:
                self.p(stmt + "\n")

    def Try(self, body):
        self.solver(body.block)

    def For(self, body):
        self.solver(body.init)
        self.p("while {}:\n".format(self.solver(body.predicate)))
        self.indent(body)
        self.solver(body.body)
        for update in body.update:
            self.p(self.solver(update) + "\n")
        self.unindent(body)

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
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        caller = calframe[3][3]
        value = body.value
        if  caller == "Type" :
            return value
        if  not self.vManager.isLocal(value):
            return "self." + value
        return value
        
    @itemFilter
    def Literal(self, body):
        value = body.value
        return value

    @itemFilter
    def Variable(self, body):
        return body.name

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
        return variable, mtype

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
        if  len(body.body) > 0: # anonymous function
            raise ClassOverriding(body)
        else:
            return "{}({})".format(mtype, ", ".join(args))

    def OverloadingInstance(self, variableDeclarator):
        variable = self.solver(variableDeclarator.variable)
        args = []
        instanceCreation = variableDeclarator.initializer
        for arg in instanceCreation.arguments:
            args.append(self.solver(arg))
        self.p("class {}({}):\n".format(variable, ", ".join(args)))
        self.indent(body)
        for stmt in instanceCreation.body:
            self.solver(stmt)
        self.unindent(body)

    def VariableDeclaration(self, body):
        mtype = self.solver(body.type)
        variables = []
        for variable in body.variable_declarators:
            variable, initializer = self.solver(variable)
            if  variable:
                self.vManager.newVariable(variable, mtype)
            if  initializer:
                variables.append("{} = {}".format(variable, initializer))
        return "{name}".format(name = ", ".join(i for i in variables))

    def VariableDeclarator(self, body):
        variable=self.solver(body.variable)
        initializer=body.initializer
        if  initializer:
            try:
                initializer = self.solver(initializer)
                return variable, initializer
            except ClassOverriding as e:
                instance = e.args[0] 
                anonymous = self.AnonymousName()
                oClass = plyj.ClassDeclaration(anonymous, instance.body, extends=instance.type)
                self.solver(oClass)
                initializer = self.solver(plyj.InstanceCreation(
                    anonymous,
                    type_arguments=instance.type_arguments,
                    arguments=instance.arguments,
                    enclosed_in=instance.enclosed_in)
                    )
                return variable, initializer
        else:
            return variable, None

    def MethodInvocation(self, body):
        name = body.name
        arguments = body.arguments
        args = []
        for arg in arguments:
            _result = self.solver(arg)
            args.append(_result)

        type_arguments = body.type_arguments

        if body.target is None:
            return "{name}({args})".format(name = name, args = ", ".join(args))
        target = self.solver(body.target)
        return "{target}.{name}({args})".format(target = target, name = name, args = ", ".join(args))
    
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

    def Shift(self, body):
        operator = self.solver(body.operator)
        lhs = self.solver(body.lhs)
        rhs = self.solver(body.rhs)
        return "({} {} {})".format(lhs, operator, rhs)

    def Cast(self, body):
        return

    def ArrayCreation(self, body):
        # ArrayCreation(type='int', dimensions=[Name(value='_arg4_length')], initializer=None)
        mtype = self.solver(body.type)
        builtinTypes = ["String", "int"]
        if  mtype in builtinTypes:
            mtype = ""
        dims = []
        for dim in body.dimensions:
            dims.append(self.solver(dim))
        dimensions = "".join("[None for _i in range({})]".format(i) for i in dims)
        initializer = body.initializer
        return "{dimensions} # {type}".format(type = mtype, dimensions = dimensions)
    
    def ArrayAccess(self, body):
        index = self.solver(body.index)
        target = self.solver(body.target)
        return "{}[{}]".format(target, index)

    def solver(self, thing, **kargs):
        if  type(thing) == type(None):
            return thing
        if  type(thing) == str:
            return thing
        return getattr(self, thing.__class__.__name__)(thing, **kargs)

    def AnonymousName(self, length = 16):
        return ''.join(random.choice(string.lowercase) for i in range(length))

    def overloadEntry(self, overloading):
        self.c("Overloading Entries")
        for method in overloading:
            self.p("\n")
            self.p("def {}(self, *args):\n".format(method))
            self.p("    fname = \"{}__\" + \"_\".join(i.__class__.__name__ for i in args)\n".format(method))
            self.p("    func = getattr(self, fname)\n")
            self.p("    func(*args)\n")
         
class Undefined(Exception):
    pass

class NotFound(Exception):
    pass

class ClassOverriding(Exception):
    pass



def dumper(body, stop = False):
    if hasattr(body, "_fields"):
        for attr in body._fields:
            print "{}={}".format(attr, type(getattr(body, attr)))
    else:
        print body

    if  stop:
        print "end"
        exit()

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    
    #inputPath = "/Users/lucas/Downloads/PackageInfo.java"
    inputPath = "/Volumes/android/sdk-source-5.1.1_r1/frameworks/base/core/java/android/content/pm/PackageInfo.java"
    with open(inputPath, "r") as inputFd:
        parser = plyj.Parser()

        root = parser.parse_file(inputFd)

        with open("output.py", "w") as outputFd:
            compiler = Compiler(outputFd)
        #compiler = Compiler(sys.stdout)
            compiler.compile(root)
