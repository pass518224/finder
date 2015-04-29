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
    #print interface_declaration.body
    for i in interface_declaration.body:
        if  type(i) == model.FieldDeclaration:
            if type(i.variable_declarators[0].initializer) == model.Additive:
                flag = i.variable_declarators[0].variable.name
                code = int(i.variable_declarators[0].initializer.rhs.value) + 1
                result[code] = flag

    return result

if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)

    inputDir  = Config.Path._IINTERFACE
    outputDir = os.path.join(Config.Path.OUT, "interface")
    filePaths = os.listdir(inputDir)

    for filePath in filePaths:
        logger.info("parsing file [{}]...".format(filePath))
        with open(os.path.join(inputDir, filePath), "r") as inputFd, open(os.path.join(outputDir, filePath), "w") as outputFd:
            result = parseTransactionCode(inputFd)
            outputFd.write(json.JSONEncoder().encode(result))

        logger.info("Parsing done")

