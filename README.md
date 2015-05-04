Finder
====

A parser for recovering the information dumped while running Android binder driver.

This project contains many tools for collecting defined interface source code in Android framework, extract semantic of variable name, translate `onTransact` function behavior into useful format.

The main purporse is to translate the raw-byte format itnto human-readable data structure.


Tools
----

###Usage

Edit `tools/Config.py` for setup the correct path of project and Android framework.
Then tools can excute at right path.

    class Path(Config):
        TOOLS       = path.dirname(path.abspath(__file__))
        PROJECT     = path.abspath(path.join( TOOLS , ".." ))
        _IINTERFACE = path.abspath(path.join( PROJECT, "_IInterface" ))
        OUT         = path.abspath(path.join( PROJECT, "out" ))

    class System(Config):
        WORKINGDIR  = path.abspath("/home/lucas/WORKING_DIRECTORY/")
        FRAMEWORK   = path.abspath(path.join(WORKINGDIR, "frameworks"))
        AIDL_CACHE   = path.abspath(path.join(WORKINGDIR, "out/target/common/obj/JAVA_LIBRARIES/framework-base_intermediates/"))
        

### Tools explaination

+ `tools/CollectIInterface.py`: Collect interface-define files into path `_IINTERFACE` of `tools/Config.py`
+ `dumpTransactionCodeFromInterface.py`: Parse files in `_IINTERFACE` and extract the name of transaction code

Dependencies
----

+ [plyj](https://github.com/musiKk/plyj)

