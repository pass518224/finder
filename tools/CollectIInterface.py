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

def fileWalker(root, excludePattern, includePattern):

    includes = r'|'.join( [fnmatch.translate(x) for x in includePattern ])
    excludes = r'|'.join( [fnmatch.translate(x) for x in excludePattern ]) or r'$.'

    for root, dirs, files in os.walk(framework ):
        dirs[:] = [d for d in dirs if not re.match(excludes, d)]    # filter excluded folders 
        dirs[:] = [os.path.join(root, d) for d in dirs]

        files = [ f for f in files if re.match(includes, f)] # filter satisfied file 
        files = [os.path.join(root, f) for f in files]

        if  len(files) > 0:
            yield files

if __name__ == '__main__':

    includePattern = ['I*.java']
    excludePattern = ['.git', 'vnc']

    framework = Config.System.FRAMEWORK

    findInterface = ""
    for files in fileWalker(framework, excludePattern, includePattern):
        for file in files:
            with open(file, "r") as fd:
                if  fd.read().find("extends IInterface") > 0:
                    t_file = file.split("/")[-1]
                    shutil.copyfile(file, os.path.join(Config.Path._IINTERFACE, t_file))
                    print file
    
    
