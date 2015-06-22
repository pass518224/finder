import logging
import os
import sys
from os import path

import plyj.parser as plyj

import Config
import Compiler
from Helper import *

logger = logging.getLogger(__name__)

def dependency_helper(solver, vManager, classes=None, interfaces=None):
    return set()

class SimpleCompiler(Compiler.Compiler):
    @Compiler.scoped
    def InterfaceDeclaration(self, body, absExtends=False):
        name, implements, decorators = getInterfaceScheme_helper(body, self.solver, self.vManager)
        if  absExtends:
            for i in range(len(implements)):
                if  self.vManager.findClass(implements[i]):
                    implements[i] = self.vManager.getFullPathByName(implements[i])

        implements = [Compiler.INITIAL_CLASS]
        self.c("# interface")
        self.p("class {name}({parent}):\n".format(name = name, parent = ", ".join(implements)), offset=-1)
        if  not body.body or len(body.body) == 0:
            self.p("pass\n")
            return

        # Field => Functions => Classes
        # -----------------------------
        # field process
        tmp = set()
        #body preprocess
        function_methods = set()
        overloading = []

        for comp in body.body:
            if  type(comp) == plyj.FieldDeclaration:
                self.solver(comp)
            elif  type(comp) == plyj.MethodDeclaration or type(comp) == plyj.ConstructorDeclaration:
                functionName = self.solver(comp.name)
                overloading.append(functionName) if functionName in function_methods else function_methods.add(functionName)
            elif type(comp) == plyj.ClassDeclaration:
                subName, subImplements, subDecorators = getClassScheme_helper(comp, self.solver, self.vManager)
                depends = deferImplement_helper(self.vManager, subImplements)
                if  len(depends) > 0:
                    self.classGraph[subName] = depends
                    self.outsideClasses[subName] = comp
                else:
                    self.solver(comp)
            elif type(comp) == plyj.InterfaceDeclaration:
                subName, subImplements, subDecorators = getInterfaceScheme_helper(comp, self.solver, self.vManager)
                depends = deferImplement_helper(self.vManager, subImplements)
                if  len(depends) > 0:
                    self.classGraph[subName] = depends
                    self.outsideClasses[subName] = comp
                else:
                    self.solver(comp)
            else:
                self.solver(comp)

        for comp in body.body:
            if  type(comp) == plyj.MethodDeclaration or type(comp) == plyj.ConstructorDeclaration:
                functionName = self.solver(comp.name)
                if  functionName in overloading:
                    self.solver(comp, appendName=True)
                else:
                    self.solver(comp)

    @Compiler.scoped
    def ClassDeclaration(self, body, absExtends=False):
        name, implements, decorators = getClassScheme_helper(body, self.solver, self.vManager)

        if  absExtends:
            for i in range(len(implements)):
                if  self.vManager.findClass(implements[i]):
                    implements[i] = self.vManager.getFullPathByName(implements[i])

        implements = [Compiler.INITIAL_CLASS]

        self.p("class {name}({parent}):\n".format(name = name, parent = ", ".join(implements)), offset=-1)

        if  len(body.body) == 0:
            self.p("pass\n")
            return

        # Field => Functions => Classes
        # -----------------------------
        # field process
        tmp = set()
        #body preprocess
        function_methods = set()
        overloading = []

        # first step scanning
        for comp in body.body:
            if  type(comp) == plyj.FieldDeclaration:
                self.solver(comp)
            elif  type(comp) == plyj.MethodDeclaration or type(comp) == plyj.ConstructorDeclaration:
                functionName = self.solver(comp.name)
                overloading.append(functionName) if functionName in function_methods else function_methods.add(functionName)
            elif type(comp) == plyj.ClassDeclaration:
                subName, subImplements, subDecorators = getClassScheme_helper(comp, self.solver, self.vManager)
                depends = deferImplement_helper(self.vManager, subImplements)
                if  len(depends) > 0:
                    self.classGraph[subName] = depends
                    self.outsideClasses[subName] = comp
                else:
                    self.solver(comp)
            elif type(comp) == plyj.InterfaceDeclaration:
                subName, subImplements, subDecorators = getInterfaceScheme_helper(comp, self.solver, self.vManager)
                depends = deferImplement_helper(self.vManager, subImplements)
                if  len(depends) > 0:
                    self.classGraph[subName] = depends
                    self.outsideClasses[subName] = comp
                else:
                    self.solver(comp)
            else:
                self.solver(comp)

        # TODO: remove outsided classes

        # append function overload entry
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
    @Compiler.scoped
    def _classMethodDeclaration(self, body, appendName = False, functionName = None):
        if  not functionName:
            functionName = self.solver(body.name)
            if  functionName == "main":
                self.mainFunction = self.vManager.getPath()
            elif functionName == "toString":
                functionName = "__str__"
        args = [Compiler.SELF_INSTANCE]
        args_type = []
        for arg in body.parameters:
            name, mtype = self.solver(arg)
            args.append(name)
            args_type.append(mtype)

        self.p("@classmethod\n", offset=-1)
        if  appendName: # function overriding
            self.p("def Oed_{}__{}({}):\n".format(functionName,
                "__".join([arg.split(".")[-1] for arg in args_type]),
                ", ".join(args)), offset = -1)
        else:
            self.p("def {}({}):\n".format(functionName, ", ".join(args)), offset = -1)
        self.p("pass\n")
        

    def FieldDeclaration(self, body):
        mtype = self.solver(body.type)
        variable_declarators = []
        for var in body.variable_declarators:
            variable, initializer = self.solver(var)
            self.vManager.newVariable(variable, mtype, isMember=True)
            if  type(var.initializer) in [plyj.Literal, plyj.Unary]:
                if  type(var.initializer) == plyj.Name:
                    for part in initializer.split("."):
                        self.fieldUsedName.add(part)
                    if  initializer in self.vManager.members:
                        initializer = self.vManager.members[initializer]
                result = "{} = {}\n".format(variable, initializer)
            else:
                result = "{} = None\n".format(variable)
            self.p(result)

if __name__ == '__main__':
    source = Config.System.LIBCORE
    out    = path.abspath(path.join(Config.Path.OUT, Config.System.VERSION, "java/java"))

    for root, dirs, files in os.walk(source):
        files = [i for i in files if i.endswith(".java")]
        for file in files:
            inPath = root 
            inFile = path.abspath(path.join(inPath, file))
            outPath = path.abspath(path.join(out, path.relpath(inPath, source)))
            outFile = path.abspath(path.join(outPath, file.replace(".java", ".py")))
            compiler = SimpleCompiler()
            parser = plyj.Parser().parse_file(inFile)
            result = compiler.compile(parser)
            
            if not os.path.exists(outPath):
                os.makedirs(outPath)
            outFd = open(outFile, "w")
            outFd.write(result)
            outFd.close()

    for root, dirs, files in os.walk(out):
        init = path.join(root, "__init__.py")
        with open(init, 'w'):
            os.utime(init, None)
