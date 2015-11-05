#!/usr/bin/env python

import plyj.parser as plyj
import Config
import logging
import os
import json
from plyj import model

logging.basicConfig()
logger = logging.getLogger(__name__)

def parseTransactionCode(inputFd):
    """parse transaction code from java source code

        @return: dict type for key:code,  value:transaction flag
    """
    parser = plyj.Parser()

    tree = parser.parse_file(inputFd)
    interface_declaration = tree.type_declarations[0]

    result = {}
    result["data"] = {}

    interfaceBody = interface_declaration.body

    #find stub class
    body = interface_declaration.body
    for node in interfaceBody:
        if type(node) == model.ClassDeclaration and node.name == "Stub": 
            body = node.body
            break

    for i in body:
        if  type(i) == model.FieldDeclaration:
            declaration = i.variable_declarators[0]
            name = declaration.variable.name
            initializer = declaration.initializer
            if type(initializer) is model.Literal:# and name.lower() is "descriptor":
                result["descriptor"] = initializer.value[1:-1]
            else:
                if type(initializer) is model.Name:
                    result["data"][name] = 1
                elif type(initializer) is model.Additive:
                    result["data"][name] = 1 + int(initializer.rhs.value)

    return result

if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)

    inputDir  = os.path.join(Config.Path._IINTERFACE, Config.System.VERSION)
    outputDir = os.path.join(Config.Path.OUT, Config.System.VERSION, "interface")
    filePaths = os.listdir(inputDir)

    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    for filePath in filePaths:
        logger.info("parsing file [{}]...".format(filePath))
        with open(os.path.join(inputDir, filePath), "r") as inputFd:
            result = parseTransactionCode(inputFd)
            result["filename"] = filePath

        with open(os.path.join(outputDir, result["descriptor"]), "w") as outputFd:
            outputFd.write(json.JSONEncoder(sort_keys = True, indent = 4).encode(result))

