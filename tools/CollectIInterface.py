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


if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)

    includePattern = ['I*.java']
    excludePattern = ['.git', 'vnc']

    framework = Config.System.FRAMEWORK
    aidl      = Config.System.AIDL_CACHE

    logger.info("Collecting system lovel interface: ")
    for file in fileWalker(framework, excludePattern, includePattern):
        with open(file, "r") as fd:
            buf = fd.read()
            if  buf.find("extends IInterface") > 0 or buf.find("extends android.os.IInterface") > 0:
                t_file = file.split("/")[-1]
                shutil.copyfile(file, os.path.join(Config.Path._IINTERFACE, t_file))
                logger.info("Matched file: [{}]".format(file))
                
    logger.info("Collecting AIDL interface: ")
    for file in fileWalker(aidl, excludePattern, ["*.java"]):
        with open(file, "r") as fd:
            buf = fd.read()
            if  buf.find("extends IInterface") > 0 or buf.find("extends android.os.IInterface") > 0:
                t_file = file.split("/")[-1]
                shutil.copyfile(file, os.path.join(Config.Path._IINTERFACE, t_file))
                logger.info("Matched file: [{}]".format(file))
