#!/usr/bin/env python

import logging
import plyj.parser as plyj
import sys

import Config

logger = logging.getLogger(__name__)


class Statement(object):
    """docstring for st"""
    def __init__(self, fd, indent = "    ", level = 0):
        self.fd = fd
        self.indent = indent
        self.level = level

    def p(self, fmt):
        self.fd.write(self.indent*self.level + fmt)
        
    def IfThenElse(self, body):
        """
         IfThenElse(
         predicate=Equality(operator='!=', lhs=Literal(value='0'), rhs=MethodInvocation(name='readInt', arguments=[], type_arguments=[], target=Name(value='data'))),
         if_true=Block(statements=[Assignment(operator='=', lhs=Name(value='_arg0'), rhs=MethodInvocation(name='createFromParcel', arguments=[Name(value='data')], type_arguments=[], target=Name(value='android.bluetooth.BluetoothDevice.CREATOR')))]),
         if_false=Block(statements=[Assignment(operator='=', lhs=Name(value='_arg0'), rhs=Literal(value='null'))]))
        """
        predicate = self.solver(body.predicate)
        self.p("if ({}):\n".format(predicate))
        self.level += 1
        self.solver(body.if_true)
        self.level -= 1
        self.p("else:\n".format(predicate))
        self.level += 1
        self.solver(body.if_false)
        self.level -= 1

    def Switch(self, body):

        value = body.expression.value
        cases      = body.switch_cases
        self.p("for _case in switch({}):\n".format(value))
        self.level += 1
        for case in cases:
            getattr(self, case.__class__.__name__)(case)
        self.level -= 1

    def SwitchCase(self, body):
        cases = body.cases
        body  = body.body

        self.p("if {case}:\n".format(case=" and ".join("case(" + i.value + ")" for i in cases)))
        self.level += 1

        for comp in body:
            fun = getattr(self, comp.__class__.__name__)
            fun(comp)

        self.level -= 1

    def Block(self, body):
        stmts = body.statements
        for stmt in stmts:
            if  type(stmt) == plyj.IfThenElse:
                self.solver(stmt)
            else:
                try:
                    self.p(self.solver(stmt) + "\n")
                except TypeError as e:
                    print stmt
                    exit()

    def Statements(self, body):
        raise Undefined

    def Statement(self, body):
        raise Undefined
    
    def VariableDeclaration(self, body):
        if  type(body.type) is not str:
            mtype = getattr(self, body.type.__class__.__name__)(body.type)
        else:
            mtype = body.type
        variables = []
        for variable in body.variable_declarators:
            variables.append(self.VariableDeclarator(variable))
        modifiers = body.modifiers
        return "{type} {name}".format(type = mtype, name = ", ".join(i for i in variables))

    
    def Assignment(self, body):
        # Assignment(operator='=', lhs=Name(value='_arg1'), rhs=MethodInvocation(name='readInt', arguments=[], type_arguments=[], target=Name(value='data')))
        operator = self.solver(body.operator)
        lhs = self.solver(body.lhs)
        rhs = self.solver(body.rhs)
        return "{lhs} {op} {rhs}".format(lhs = lhs, op = operator, rhs = rhs)


    def Return(self, body):
        return "return {}".format(self.solver(body.result))

    """ none print"""

    def Name(self, body):
        if  type(body) is str:
            return body
        return body.value

    def Type(self, body):
        if  type(body) is str:
            return body
        type_arguments=body.type_arguments
        enclosed_in=body.enclosed_in
        dimensions=body.dimensions
        return self.Name(body.name)

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

    def VariableDeclarator(self, body):
        variable=self.solver(body.variable)
        initializer=body.initializer
        if  initializer:
            initializer = self.solver(initializer)
            return "{} = {}".format(variable, initializer)
        else:
            return variable

    def MethodInvocation(self, body):
        name = body.name
        arguments = body.arguments
        args = []
        for arg in arguments:
            fun = getattr(self, arg.__class__.__name__)
            args.append(fun(arg))
        type_arguments = body.type_arguments
        if  type(body.target) == plyj.Name:
            target = self.Name(body.target)
        elif body.target == "this":
            target = "self"
        else:
            target = body.target

        return "{target}.{name}({args})".format(target = target, name = name, args = ", ".join(i for i in args))
    
    def Equality(self, body):
        #Equality(operator='!=', lhs=Literal(value='0'), rhs=MethodInvocation(name='readInt', arguments=[], type_arguments=[], target=Name(value='data')))
        operator = self.solver(body.operator)
        lhs = self.solver(body.lhs)
        rhs = self.solver(body.rhs)
        return "{} {} {}".format(lhs, operator, rhs)



    def parse_body(self, body):
        for comp in body:
            name = comp.__class__.__name__
            fun = getattr(self, name)
            fun(comp)

    def solver(self, thing):
        if  type(thing) == str:
            return thing
        logger.debug(self.indent*self.level + thing.__class__.__name__)
        return getattr(self, thing.__class__.__name__)(thing)
         
class Undefined(Exception):
    pass

def translator(inputPath):
    """ translate AIDL-generated java file into python file"""
    parser = plyj.Parser()

    root = parser.parse_file(inputPath)
    body = root.type_declarations[0].body

    # search class 'Stub'
    for comp in body:
        if  hasattr(comp, "name"):
            if  comp.name == "Stub":
                classStub = comp
                break

    for method in classStub.body:
        if  type(method) == plyj.MethodDeclaration and method.name == "onTransact":
            methodTransact = method
            break

    Statement(sys.stdout).parse_body(methodTransact.body)


if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    inputPath = "/home/lucas/Downloads/IBluetooth.java"

    translator(inputPath)
