import logging
import re

import plyj.parser as plyj
import Compiler

logger = logging.getLogger(__name__)

def match(comp, selector):
    """
    selector match pattern
    TYPE_OF_PLYJ := DESCRIPTION | nil

    DESCRIPTION := ATTRIBUTE

    ATTRIBUTE := ATTR_NAME
                 (ATTR_NAME = ATTR_VAL)
    """
    condition = selector[1]
    if  condition.isMatch(comp):
        selector.pop(0)
        selector.pop(0)
        return True
    return False

def startHandler(self, root, selector):
    match(root, selector)
    self._doSearch(root, selector)

def childHandler(self, root, selector):
    if  match(root, selector):
        return self._doSearch(root, selector)
    else:
        return 

def desHandler(self, root, selector):
    match(root, selector)
    self._doSearch(root, selector)

class Selector(object):
    """docstring for Selector"""
    def __init__(self, filePath):
        self.root = plyj.Parser().parse_file(filePath)
        self.founds = []

    def query(self, selector):
        selector = self._child(selector)
        selector.insert(0, "^")
        for i in range(1,len(selector), 2):
            selector[i] = Comparator(selector[i])
        logger.debug("query: {}".format(selector))
        self.search(self.root, list(selector))
        return self.founds

    def _child(self, selector):
        selector = selector.replace(">", " > ")
        #selector = selector.replace(".", " . ")
        selector = selector.split(" ")
        return selector

    def search(self, root, selector):
        handler = self.relationHandler(selector[0])
        result = handler(self, root, selector)

    def _doSearch(self, root, selector):
        if  len(selector) == 0:
            self.founds.append(root)
            return

        for comp in self.child(root):
            result = self.search(comp, list(selector))
        return


    def select(self, selector):
        """description for advanced selection"""
        pass

    def relationHandler(self, relator):
        """
        return relation handler from relator
        ">" : must be directly child
        " " : assendent are ok
        """
        if  relator == ">":
            return childHandler
        elif relator == ".":
            return desHandler
        elif relator == "^":
            return startHandler
        else:
            raise Exception("Invalid relator: {}".format(relator))

    # select functions
    def child(self, body):
        ctype = type(body)
        if  ctype == plyj.CompilationUnit:
            return body.type_declarations
        elif ctype in [plyj.ClassDeclaration, plyj.InterfaceDeclaration, plyj.MethodDeclaration]:
            result = body.body
            if  result == None:
                return []
            return result
        else:
            return []
        
class Comparator(object):
    """Unit to compare the plyj element"""
    def __init__(self, selector):
        self.comparator = self.parse(selector)
        self.compiler = Compiler.Compiler()

    def parse(self, condition):
        """docstring for parse"""
        comparator = {}
        lindex = condition.find("[")
        if  lindex > 0:
            comparator["type"] = condition[:lindex]
            self.setattr(comparator, condition[lindex:])
        else:
            comparator["type"] = condition
        return comparator

    def setattr(self, comparator, condition):
        rindex = condition.find("]")
        if  rindex <= 0:
            raise SyntaxError("invalid syntax: unfound symmetry \"]\" ")

        lindex = condition.find("[")
        condition = condition[lindex+1:rindex]
        eqIndex = condition.find("=")
        if  eqIndex > 0:
            attrs = re.findall(r'(\w+)([\^\*\$=]+)([\w\.]+)', condition)[0]
            comparator["attr"] = attrs[0]
            comparator["relator"] = attrs[1]
            comparator["value"] = attrs[2]
        else:
            comparator["attr"] = condition

    def isMatch(self, comp):
        cType = comp.__class__.__name__
        comparator = self.comparator
        if "type" in comparator and cType != comparator["type"]:
            return False
        elif "attr" in comparator:
            attr = comparator["attr"]
            if  not hasattr(comp, attr) or getattr(comp, attr) == None:
                return False
            if "relator" in comparator and "value" in comparator:
                relator = comparator["relator"]
                value   = comparator["value"]
                compValue = solve(getattr(comp, attr))
                if  relator == "=":
                    if  value != compValue:
                        return False
                elif relator == "^=":
                    if not compValue.startswith(value):
                        return False
                elif relator == "$=":
                    if  not compValue.endswith(value):
                        return False
                elif relator == "*=":
                    if  value not in compValue:
                        return False
                else:
                    raise SyntaxError("Unknown relator: {}".format(relator))
        return True


    def __str__(self):
        return str(self.comparator)

    def __repr__(self):
        return str(self.comparator)
        
def solve(attrs):
    if  type(attrs) == list:
        result = []
        for attr in attrs:
            result.append(solve.compiler.solver(attr))
        return result
    else:
        return solve.compiler.solver(attrs)
solve.compiler = Compiler.Compiler()
                

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    compiler = Compiler.Compiler()
    a = Selector("/Volumes/android/sdk-source-5.1.1_r1/frameworks/base/core/java/android/content/ClipData.java")
    result = a.query("ClassDeclaration")
    print "=============="
    for i in result:
        print i
    print "=============="
    """
    match("", "ClassDeclaration[name^=Proxy]")
    """
