import logging
import re
import plyj.parser as plyj
from plyj.model import  CompilationUnit

import Config

logger = logging.getLogger(__name__)

class SchemeBuilder(object):
    def __init__(self, searchPath="", cachePath=""):
        """
        quickly traverse class layout
        """
        self.cachePath = cachePath
        self.searchPath = Config.system.JAVA_LIBS + list(searchPath)
        logger.info("Construct SchemeBuilder with:\n\tsearchPath: {}, cachePath: {}".format(searchPath, cachePath))

    def _search(self, className):
        """search file by given class name
        @className: className we want to search for, only accept format "class1.class2.class3" ...
        @return: absolute file path
            """
        pass

    def build(self, className):
        """directly build with given file name"""
        pass

    def cache(self):
        """serialize parsed result to cache file"""
        pass

    def uncache(self, cachePath=""):
        """unserialize from cache file"""
        pass

def _buildHelper(body, vManager):
    MACRO_PATTERN = r"[A-Z_]+"
    upperPattern = re.compile(MACRO_PATTERN)
    for comp in body.body:
        if  type(comp) in [plyj.MethodDeclaration, plyj.ConstructorDeclaration]:
            vManager.newScope(comp)
            vManager.leaveScope(comp)
        elif type(comp) == plyj.ClassDeclaration or type(comp) == plyj.InterfaceDeclaration:
            vManager.newScope(comp)
            if  comp.body != None and len(comp.body) > 0:
                _buildHelper(comp, vManager)
            vManager.leaveScope(comp)
        elif type(comp) == plyj.FieldDeclaration:
            for variable in comp.variable_declarators:
                name = variable.variable.name
                if  upperPattern.match(name):
                    vManager.addMacro(name)


def buildHelper(plyTree, vManager):
    """build helper: for builing exist plyj tree with given VariableManager"""
    if  type(plyTree) != CompilationUnit:
        raise Exception("Input is not a CompilationUnit, given {}".format(type(plyTree)))
    for comp in plyTree.type_declarations:
        if type(comp) in [plyj.MethodDeclaration, plyj.ConstructorDeclaration, plyj.ClassDeclaration, plyj.InterfaceDeclaration]:
            vManager.newScope(comp)
            _buildHelper(comp, vManager)
            vManager.leaveScope(comp)


