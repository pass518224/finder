import pytest
from os import path
import sys
mpath = path.join(path.dirname(__file__), "../")
sys.path.insert(0, mpath)

from tools import Includer

root = "/Volumes/android/sdk-source-5.1.1_r1/frameworks/base/core/java"
file = root + "/android/content/pm/PackageInfo.java"

@pytest.fixture
def includer():
    includer = Includer.Includer(root, file)
    return includer

class TestUtils(object):
    def test_path2pkg(self, includer):
        pkg =  "android.os.Parcel"
        path = "/Volumes/android/sdk-source-5.1.1_r1/frameworks/base/core/java/android/os/Parcel.java"
        assert Includer.path2pkg(root, path) == pkg

    def test_pkg2path(self, includer):
        pkg =  "android.os.Parcel"
        path = "/Volumes/android/sdk-source-5.1.1_r1/frameworks/base/core/java/android/os/Parcel.java"
        assert Includer.pkg2path(root, pkg) == path
