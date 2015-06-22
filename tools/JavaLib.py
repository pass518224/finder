
def method(fun):
    def transform(self, body):
        result = fun(self, body)
        functionName = result.split("(")[0]
        if  functionName in methodMap:
            return result.replace(functionName, methodMap[functionName])
        return result
    return transform

methodMap = {
        "System.out.println": "print"
}

def builtinTypes(mtype):
    if  mtype in builtinMap:
        return builtinMap[mtype] + "()"
    return "None"

builtinMap ={
        "byte": "bytes",
        "int": "int",
        "long": "int",
        "String": "str",
        "str": "str",
        "double": "float",
        "float": "float",
        "Float": "float",
        "boolean": "bool",
}

builtinClass = set([
    "AccessibleStreamable",
    "AdapterActivatorOperations",
    "Callable",
    "Cloneable",
    "Closeable",
    "Comparable",
    "Comparator",
    "Compilable",
    "Destroyable",
    "Externalizable",
    "Flushable",
    "Formattable",
    "Invocable",
    "ItemSelectable",
    "Iterable",
    "JMXAddressable",
    "Joinable",
    "Pageable",
    "Printable",
    "Readable",
    "Referenceable",
    "Refreshable",
    "Runnable",
    "Scrollable",
    "Serializable",
    "StateEditable",
    "Streamable",
    "Transferable",
    "TypeVariable",
    # dynamic catched builting java libraries
    "ThreadLocal",
])
