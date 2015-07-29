#!/usr/bin/env python2.7
"""
Collect IInterface java source in android framework
move from ANDROID TO _IINTERFACE directory
"""

import Config
import logging
import fnmatch
import shutil
import os
import re

logger = logging.getLogger(__name__)

def fileWalker(travelPath, excludePattern, includePattern):

    includes = r'|'.join( [fnmatch.translate(x) for x in includePattern ])
    excludes = r'|'.join( [fnmatch.translate(x) for x in excludePattern ]) or r'$.'

    result = []
    for root, dirs, files in os.walk(travelPath ):
        dirs[:] = [d for d in dirs if not re.match(excludes, d)]    # filter excluded folders 
        dirs[:] = [os.path.join(root, d) for d in dirs]

        files = [ f for f in files if re.match(includes, f)] # filter satisfied file 
        files = [os.path.join(root, f) for f in files]

        result += files
    return result

def recursiveCopy(source, target, excludePattern, includePattern):
    for file in fileWalker(source, excludePattern, includePattern):
        with open(file, "r") as fd:
            buf = fd.read()
            if  buf.find("public BpInterface") > 0 and buf.find("onTransact") > 0:
                t_file = file.split("/")[-1]
                shutil.copyfile(file, os.path.join(target, t_file))
                logger.info(" o {}".format(file))


if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)

    includePattern = ['*.cpp']
    excludePattern = ['.git', 'vnc']

    hardware = os.path.join( Config.Path._HARDWARE, Config.System.VERSION)
    if not os.path.exists(hardware):
        os.makedirs(hardware)

    logger.info("Collecting hardware interface: ")
    root = Config.System.FRAMEWORK
    recursiveCopy(root, hardware, excludePattern, includePattern)
    root = Config.System.PACKAGES
    recursiveCopy(root, hardware, excludePattern, includePattern)
    root = Config.System.SYSTEM
    recursiveCopy(root, hardware, excludePattern, includePattern)
