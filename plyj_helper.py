#!/usr/bin/env python

import plyj.parser as plyj
from plyj import model

def dumper(name, object, indent=0, indent_prefix = "    "):
    if  hasattr(object, "_fields"):
        print "{indent}{r_name}:".format( indent = indent_prefix*indent, r_name = name)
        indent += 1
        for attrName in object._fields:
            newObject = getattr(object, attrName)
            dumper(attrName, newObject, indent = indent)
    elif type(object) is list:
        if  len(object) > 0:
            print "{indent}{r_name}: [".format( indent = indent_prefix*indent, r_name = name)
            for obj in object:
                dumper(obj.__class__.__name__, obj, indent=indent+1)
            print "{indent}]".format( indent = indent_prefix*indent)
        else:
            print "{indent}{r_name}: []".format( indent = indent_prefix*indent, r_name = name)
    else:
        print "{indent}{r_name}: '{val}'".format( indent = indent_prefix*indent, r_name = name, val = str(object))

if __name__ == '__main__':
    filePath = "/home/lucas/WORKING_DIRECTORY/kernel/goldfish/Finder/_IInterface/IActivityManager.java"
    parser = plyj.Parser()
    tree = parser.parse_file(file(filePath))    # syntax tree root
    #print tree

    dumper(tree.__class__.__name__, tree)
    
