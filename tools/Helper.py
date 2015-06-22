import keyword 
import logging
import random
import string

from collections import deque
import JavaLib

logger = logging.getLogger(__name__)


# solver needed
def dependency_helper(solver, vManager, classes=None, interfaces=None):
    implements = set()
    if  classes:
        extName = solver(classes)
        if  extName.endswith("Exception"):
            extName = "Exception"
        if  extName in vManager.reversedClassPaths:
            extName = vManager.reversedClassPaths[extName]
        if  extName == "Creator":
            extName = "Parcelable.Creator"
        implements.add(extName)
    if  interfaces:
        for interface in interfaces:
            extName = solver(interface)
            if  extName.endswith("Exception"):
                extName = "Exception"
            if  extName in vManager.reversedClassPaths:
                extName = vManager.reversedClassPaths[extName]
            if  extName == "Creator":
                extName = "Parcelable.Creator"
            implements.add(extName)

    return list(implements - JavaLib.builtinClass)

def getClassScheme_helper(cls, solver, vManager):
    name = solver(cls.name)
    implements = dependency_helper(solver, vManager, classes=cls.extends)
    return name, implements, {}

def getInterfaceScheme_helper(cls, solver, vManager):
    name = solver(cls.name)
    implements = dependency_helper(solver, vManager)
    return name, implements, {}

# solver needless
def keywordReplace_helper(string):
    """keyword replacement"""
    strs = string.split(".")
    strs = map(lambda i: "_" + i if keyword.iskeyword(i) else i, strs)
    return ".".join(strs)

ANONYMOUS_PREFIX = "ANONY_" 
def AnonymousName_helper(length = 16):
    return ANONYMOUS_PREFIX+ ''.join(random.choice(string.lowercase) for i in range(length))

def deferImplement_helper(vManager, implements):
    depends = []
    for i in range(len(implements)):
        if  vManager.findClass(implements[i]):
            depends.append(implements[i])
    return depends

"""
# Simple:
# a --> b
#   --> c --> d
#   --> d 
graph1 = {
    "a": ["b", "c", "d"],
    "b": [],
    "c": ["d"],
    "d": []
}
"""
GRAY, BLACK = 0, 1
def topological(graph):
    order, enter, state = deque(), set(graph), {}
 
    def dfs(node):
        state[node] = GRAY
        for k in graph.get(node, ()):
            sk = state.get(k, None)
            if sk == GRAY: raise ValueError("cycle\n"+str(graph))
            if sk == BLACK: continue
            enter.discard(k)
            dfs(k)
        order.appendleft(node)
        state[node] = BLACK
 
    while enter: dfs(enter.pop())
    return order
