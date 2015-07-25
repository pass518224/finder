#!/usr/bin/env python
"""
Compare interface files between android version
"""
import logging
import sys
import os
import simplejson as json
import collections
from os import path

sys.path.append("../tools")

import Config
import Selector
import plyj.parser as plyj

logger = logging.getLogger(__name__)

class VersionContainer(object):
    """used for container all version data"""
    def __init__(self, versionName, cache=True):
        self.versionName = versionName
        self.cachePath = absjoin(Config.Path.EVAL, "RPCs."+versionName)

        if  cache and os.path.isfile(self.cachePath):
            logger.info("Find cache {}".format(self.cachePath))
            with open(self.cachePath, "rw") as cacheFd:
                data = cacheFd.read()
                self.fileTable = json.loads(data)
        else:
            self.fileTable = self.summaryMethods()
            self.cache()

        self.indexSet = self.indexKeys(self.fileTable)
        
    def indexKeys(self, tree):

        def _indexKeys(keySet, tree, prefix):
            for key, val in tree.iteritems():
                if type(val) == str:
                    keySet.add(prefix + "." + key)
                elif type(val) == dict:
                    _indexKeys(keySet, val, prefix + "." + key)

        keySet = set()
        for key, val in tree.iteritems():
            if type(val) == str:
                keySet.add(key)
            elif type(val) == dict:
                _indexKeys(keySet, val, key)
        return keySet

    def cache(self):
        #prevent none exist directories
        if not os.path.exists(Config.Path.EVAL):
            os.makedirs(Config.Path.EVAL)

        with open(self.cachePath, "w") as outFd:
            outFd.write(json.dumps(self.fileTable, indent=4, sort_keys=True))

    def summaryMethods(self):
        iFiles, nFiles = self.getInterfaces(self.versionName)
        fileTable = self.parseFiles(self.versionName, nFiles)
        fileTable.update(self.parseFiles(self.versionName, iFiles))
        return fileTable

    def getInterfaces(self, vName):
        """
        get interfaces file paths with given version name
        @vName: complete version name
        @return: interface file paths, native interface file paths
        """
        interface = absjoin( Config.Path._IINTERFACE, vName)
        nativeStub = absjoin( Config.Path._NATIVE_STUB, vName)

        if not path.isdir(interface):
            raise Exception("Not found interface of {}".format(interface))

        if not path.isdir(nativeStub):
            raise Exception("Not found native file of {}".format(vName))

        iFiles = os.listdir(interface)
        if  len(iFiles) == 0:
            raise Exception("empty dir: {}".format(interface))
        iFiles = map(lambda x:absjoin(interface, x), iFiles)

        nFiles = os.listdir(nativeStub)
        if  len(nFiles) == 0:
            raise Exception("empty dir: {}".format(nativeStub))
        nFiles = map(lambda x:absjoin(nativeStub, x), nFiles)

        logger.info("[{}] Find interface: {}, nativeStub: {}".format(vName, len(iFiles), len(nFiles)))
        return iFiles, nFiles

    def parseParameters(self, params):
        parameters = []
        for para in params:
            mtype = Selector.solve(para.type)
            var   = Selector.solve(para.variable)
            parameters.append((mtype, var))
        return parameters

    def interfaceFinder(self, filePath):
        nativeMethodPath = "ClassDeclaration[name$=Proxy]>MethodDeclaration[throws*=RemoteException]"
        result = Selector.Selector(filePath).query(nativeMethodPath)
        if len(result) == 0:
            AIDLMethodPath = "ClassDeclaration[name=Stub]>ClassDeclaration[name=Proxy]>MethodDeclaration[throws*=android.os.RemoteException]"
            result = Selector.Selector(filePath).query(AIDLMethodPath)
        functions = {}
        for method in result:
            name = Selector.solve(method.name)
            parameters = self.parseParameters(method.parameters)
            functions[name] = ", ".join(i[0]+" "+i[1] for i in parameters)
        return functions

    def parseFiles(self, version, files):
        logger.info("start to parse file in {}".format(version))
        fileTable = {}
        for file in files:
            if  not file.endswith(".java"):
                continue
            logger.debug(" o {}".format(file))
            filename = file.split("/")[-1].strip(".java")
            fileTable[filename] = self.interfaceFinder(file)
        return fileTable

    def compare(self, container):
        print "total of 1 {}".format(len(set_1))
        print "total of 2 {}".format(len(set_2))
        print "1 more {}".format(len(set_1 - set_2))
        print "2 more {}".format(len(set_2 - set_1))
        print "intersection {}".format( len(set_1 & set_2))
        print "union {}".format( len(set_1.union(set_2)))

    def reportWith(self, container):
        reportPath = absjoin(Config.Path.EVAL, "RPC_report")
        #prevent none exist directories
        if not os.path.exists(reportPath):
            os.makedirs(reportPath)
        
        logger.info("dump {} only functions...".format(self.versionName))
        with open(absjoin(reportPath, "{}_only".format(self.versionName)), "w") as fd:
            tree = self.pathsToDict(self.indexSet - container.indexSet, self.fileTable)
            fd.write(jsonDump(tree))

        logger.info("dump {} only functions...".format(container.versionName))
        with open(absjoin(reportPath, "{}_only".format(container.versionName)), "w") as fd:
            tree = self.pathsToDict(container.indexSet - self.indexSet , container.fileTable)
            fd.write(jsonDump(tree))

        logger.info("dump intersection with different function declaratino")
        with open(absjoin(reportPath, "intersection"), "w") as fd:
            count = 0
            intersection = container.indexSet & self.indexSet
            myTree = self.pathsToDict(intersection , self.fileTable)
            otherTree = self.pathsToDict(intersection , container.fileTable)
            result = self.compare(myTree, otherTree)
            for descriptor, interfaces in result.iteritems():
                if  len(interfaces) == 0 :
                    continue
                fd.write("{}:\n".format(descriptor))
                for interface, val in interfaces.iteritems():
                    count += 1
                    myType, oType = val.split(" / ")
                    fd.write("    {}:\n".format(interface))
                    fd.write("      {}:({})\n".format(self.versionName, myType))
                    fd.write("      {}:({})\n\n".format(container.versionName, oType))
                fd.write("\n")

        logger.info("dump final report")
        with open(absjoin(reportPath, "report"), "w") as fd:
            fd.write("# of {} : {}\n".format(self.versionName, len(self.indexSet)))
            fd.write("# of {} : {}\n".format(container.versionName, len(container.indexSet)))
            fd.write("{} only: {}\n".format(self.versionName, len(self.indexSet - container.indexSet)))
            fd.write("{} only: {}\n".format(container.versionName, len(container.indexSet - self.indexSet)))
            fd.write("union: {}\n".format(len(container.indexSet.union(self.indexSet))))
            fd.write("intersection: {}\n".format(len(container.indexSet & self.indexSet)))
            fd.write("intersection with different function prototype: {}\n".format(count))

    def compare(self, myTree, oTree):
        result = collections.defaultdict(dict)

        def _walk(rdict, myTree, oTree):
            for key, val in myTree.iteritems():
                if  type(val) == str:
                    if  myTree[key] != oTree[key]:
                        rdict[key] = "{} / {}".format(myTree[key], oTree[key])
                elif type(val) == dict:
                    _walk(rdict[key], myTree[key], oTree[key])

        for key in myTree:
            _walk(result[key], myTree[key], oTree[key])
        return result

    def pathsToDict(self, sets, table):
        result = collections.defaultdict(dict)
        for paths in sets:
            node = table
            pointer = result
            for key in paths.split("."):
                if  type(node[key]) == str:
                    pointer[key] = node[key]
                elif type(node[key]) == dict:
                    pointer = pointer[key]
                    node = node[key]
                else:
                    raise Exception("should not have other type")
        return result

def absjoin(*args):
    return path.abspath( path.join(*args))

def jsonDump(ds):
    return json.dumps(ds, indent=4, sort_keys=True)

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    v1 = VersionContainer("android-4.4.3_r1")
    v2 = VersionContainer("android-5.1.1_r1")

    v1.reportWith(v2)
