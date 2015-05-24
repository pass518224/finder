
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
        "double": "float",
        "float": "float",
        "boolean": "bool",
}
