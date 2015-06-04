import subprocess
from os import path
import sys
mpath = path.join(path.dirname(__file__), "../")
sys.path.insert(0, mpath)

import pytest
import plyj.parser as plyj

from tools import Compiler

def javaOutput(tmpdir, className):
    cmd = "javac -d {tmp} {mpath}/test/testcases/{c}.java && java -cp {tmp} {c}".format(tmp=tmpdir, mpath=mpath, c=className)
    compile_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return compile_process.stdout.read(100)

def pythonOutput(tmpdir, className):
    parser = plyj.Parser().parse_file("{}/test/testcases/{}.java".format(mpath, className))
    target = path.join(str(tmpdir), className + ".py")
    with open(target, "w") as tfd:
        Compiler.Compiler(tfd).compile(parser)
    cmd = "python {}".format(target)
    pProcess = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return pProcess.stdout.read(100)


class TestClass(object):
    def test_Class00(self, tmpdir):
        className = "Class00"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_Class01(self, tmpdir):
        className = "Class01"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_Class02(self, tmpdir):
        className = "Class02"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_Class03(self, tmpdir):
        className = "Class03"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_Class04(self, tmpdir):
        className = "Class04"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_Class05(self, tmpdir):
        className = "Class05"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_Class06(self, tmpdir):
        className = "Class06"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_Class07(self, tmpdir):
        className = "Class07"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_Class08(self, tmpdir):
        className = "Class08"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_Class09(self, tmpdir):
        className = "Class09"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_Class12(self, tmpdir):
        className = "Class12"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

class TestIf(object):
    def test_If0(self, tmpdir):
        className = "If0"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_If1(self, tmpdir):
        className = "If1"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_If2(self, tmpdir):
        className = "If2"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_If3(self, tmpdir):
        className = "If3"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_If4(self, tmpdir):
        className = "If4"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_If5(self, tmpdir):
        className = "If5"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_If6(self, tmpdir):
        className = "If6"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_If7(self, tmpdir):
        className = "If7"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_If8(self, tmpdir):
        className = "If8"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

class TestInterface(object):
    def test_Interface0(self, tmpdir):
        className = "Interface0"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_Interface1(self, tmpdir):
        className = "Interface1"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_Interface2(self, tmpdir):
        className = "Interface2"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

class TestForLoop(object):
    def test_ForLoop0(self, tmpdir):
        className = "ForLoop0"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_ForLoop1(self, tmpdir):
        className = "ForLoop1"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_ForLoop2(self, tmpdir):
        className = "ForLoop2"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_ForEach0(self, tmpdir):
        className = "ForEach0"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

class TestProperty(object):
    def test_Property0(self, tmpdir):
        className = "Property0"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_Property1(self, tmpdir):
        className = "Property1"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

class TestWhile(object):
    def test_While0(self, tmpdir):
        className = "While0"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_While1(self, tmpdir):
        className = "While1"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_While2(self, tmpdir):
        className = "While2"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

class TestInstance(object):
    def test_instance0(self, tmpdir):
        className = "InstanceCreation0"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_instance1(self, tmpdir):
        className = "InstanceCreation1"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_instance2(self, tmpdir):
        className = "InstanceCreation2"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

class TestIncrement(object):
    def test_increment0(self, tmpdir):
        className = "Increment0"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

    def test_increment1(self, tmpdir):
        className = "Increment1"
        assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

def test_keyword0(tmpdir):
    className = "Keyword0"
    assert javaOutput(str(tmpdir), className) == pythonOutput(str(tmpdir), className)

