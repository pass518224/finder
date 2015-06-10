#!/usr/bin/env python

import logging
import os
from os import path
import copy

import Config
import Includer
import Compiler

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    out = path.join(Config.Path.OUT, Config.System.VERSION, "java")
    source = Config.System.JAVA_POOL
    if not os.path.exists(out):
        os.mkdir(out)

    file = Includer.absjoin(source, "android/content/pm/PackageInfo.java")
    #file = Includer.absjoin(source, "android/hardware/camera2/utils/BinderHolder.java")
    #file = Includer.absjoin(source, "android/app/EnterTransitionCoordinator.java")

    compiler = Compiler.Compiler()
    result = compiler.compilePackage(source, file)
    imports = compiler.imports

    targetFile = path.join(out, path.relpath(file, source)).replace(".java", ".py")
    targetDir = path.dirname(targetFile)

    if not os.path.exists(targetDir):
        os.makedirs(targetDir)

    with open(targetFile, "w") as targetFd:
        targetFd.write(result)
    
    solvedPkgs = set(Includer.path2pkg(source, file))
    while len(imports) > 0:
        logger.info("dependency: []".format(", ".join(imports)))
        toSolve = copy.copy(imports)

        for pkg in toSolve:
            solvedPkgs.add(pkg)
            imports.remove(pkg)

            if  pkg.split(".")[0] == "java":
                logger.info("builtin lib: {}".format(pkg))
                continue

            file = Includer.pkg2path(source, pkg)

            targetFile = path.join(out, path.relpath(file, source)).replace(".java", ".py")
            targetDir = path.dirname(targetFile)
            
            if  os.path.isfile(targetFile):
                logger.info("Solved file<<<END>>> // {}".format(file))
                continue
            else:
                logger.info("new file<<<START>>> // {}".format(file))

            if  not os.path.isfile(file):
                logger.warn("Unknown file: {}".format(file))
                continue

            compiler = Compiler.Compiler()
            result = compiler.compilePackage(source, file)
            newDiscover = compiler.imports - solvedPkgs
            if  len(newDiscover) > 0:
                logger.info("new discover: {}".format(", ".join(newDiscover)))
                imports = imports.union(newDiscover)


            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
                
            with open(targetFile, "w") as targetFd:
                targetFd.write(result)

    for root, dirs, files in os.walk(out):
        init = path.join(root, "__init__.py")
        with open(init, "w") as fd:
            pkgs = set()
            for d in dirs:
                fd.write("import {}\n".format(d))
                pkgs.add(d)
            for file in files:
                name = file.split(".")[0]
                if  name != "__init__":
                    pkgs.add(name)
            for pkg in pkgs:
                fd.write("from {} import *\n".format(pkg))
    """

    for root, dirs, files in os.walk(out):
        init = path.join(root, "__init__.py")
        with open(init, 'w'):
            os.utime(init, None)
    """

    print imports


        
