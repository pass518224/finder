Finder
====

A parser generator for recovering the ICC (inter-component communication) data. 
The ICC data are gathered through hooking Android binder driver .

This project contains the tools for interface source code collection, 
 variable name semantics extraction, and function behavior translation.
The interface source code is from Android Framework so far. Our work shall 
include most of the interfaces of system components so that we can deal with
basic ICC data. The function behaviors we should considered are in every 
`onTransact` function, locating in every ICC component.

Without directly running these Java code of ICC components, Finder generates 
python parsers corresponding to ICC components. The main purporse of parsers is 
to translate the ICC data, raw-byte, into data structures, human-readable. 
These data structures are also useful for forensic and static analysis.



Tools
----

#### `tools/Config.py`
Config the path of this project and Android framework for interfaces collection.

    class Path(Config):
        TOOLS       = path.dirname(path.abspath(__file__))
        PROJECT     = path.abspath(path.join( TOOLS , ".." ))
        _IINTERFACE = path.abspath(path.join( PROJECT, "_IInterface" ))
        OUT         = path.abspath(path.join( PROJECT, "out" ))

    class System(Config):
        WORKINGDIR  = path.abspath("/home/lucas/WORKING_DIRECTORY/")
        FRAMEWORK   = path.abspath(path.join(WORKINGDIR, "frameworks"))
        AIDL_CACHE   = path.abspath(path.join(WORKINGDIR, "out/target/common/obj/JAVA_LIBRARIES/framework-base_intermediates/"))
        

#### `tools/CollectIInterface.py`
Collect interface-define files into path `_IINTERFACE` of `tools/Config.py`

#### `tools/dumpTransactionCodeFromInterface.py`
Parse files in `_IINTERFACE` and extract the name of transaction code

Transaction features
----

#### Import Packages

Python parsers include/import other parsers when a **instance** or **extends 
(implements)** is created. A instance is a Java Class. The source code of the 
class will be translated into a Python module. The class extent by other classes
will also has a Python module. The Python module contains the translated Python 
code for control-flow dependent functions.

Whenever a Java class is refered, Finder shall create and include the 
corresponding parser.


Transaction problems
----

#### Java built-in packages

Java have many built-in packages, we need a standard support of these libraries.

#### Unary operations
Usually are used in loop.

In c/c++ coding. But python dont have these features.
`a++`, `if (i++ > 0)` are not supported in python.
Python doesn't support `i++` or `++i` type unary operator.
Instead of this `i += 1`.

#### Assignment in condition

The main problem is java style conditions

    while (((event = in.next()) != XmlPullParser.END_DOCUMENT)) {
        if (event == XmlPullParser.START_TAG) {
            name = in.getName();
        }
    }

This case have an assignment then comparison. 


#### Multi-times assignment 
It is also not supported by Python.

    int a = b = 100

Instead of previous case, we translate the above code into the follows:

    b = 100
    int a = b


#### Self-instantiation

>This is to-do

#### Extend outer class

java has a feature to extend outer class like:

    public abstract class CharacterStyle {

        public static CharacterStyle () {
            return new Passthrough(cs);
        }

        class Passthrough extends CharacterStyle {
            private CharacterStyle mStyle;

            public CharacterStyle getUnderlying() {
                return mStyle.getUnderlying();
            }
        }
    }

#### Anonymous Class

Java has anonymous class that let you override the sub-part without explicit declaring a new one
like `PackageInfo.java`

    public static final Parcelable.Creator<PackageInfo> CREATOR
            = new Parcelable.Creator<PackageInfo>() {
        @Override
        public PackageInfo createFromParcel(Parcel source) {
            return new PackageInfo(source);
        }

        @Override
        public PackageInfo[] newArray(int size) {
            return new PackageInfo[size];
        }
    };

#### Function overloading

Java have a feature of function overloading. 
The caller will call the corresponding function base on the parameters types. 
This feature call **function overloading**.

    public Intent putExtra(String name, Serializable value) {
        ...
    }

    public Intent putExtra(String name, boolean[] value) {
        ...
    }

    public Intent putExtra(String name, byte[] value) {
        ...
    }

Python also have this feature. But it have different properties.

    def function(para1, para2 = None, para3 = 0):
        pass

    def function(*args):
        pass

    def function(**kargs):
        pass

But the usage of Python is different with java.
So we have to implement an adaptor to convert the type into corresponding function interface.

#### Casted variable as overloading input

#### Cycle import


Limitation
----

#### Hardware RPC

Most of Andoird PRC are constructed by Java code which was translated by AIDL or hand craft.

Some of these are written directly with C/CPP and compile to a user space services.
These kind of services and almost related to hardware control, Audio control. The differents
between Java VM level serivces is the serices are written by C/CPP and directly run as a native 
program without dalvik VM. Our work aim to focus Java-level serivces. So we still catch these 
ICC transaction but filter out these kinds serivces. 

We filter out these services while translating. Hard coded in `lib/TransactionManager.py`.

#### From Java to Cpp code

Finder does not handle the dependencies from Java VM to native CPP.

For some performance concern or the need of low level operation, some Android functions
implemented with C/CPP. The file `/frameworks/base/core/jni/android_os_Parcel.cpp` 
descript the JNI interface. It connect Java function name to native function always 
with prefix of **native[FUNCTION_NAME]**.

As previous description. Finder handel only Java level services/program. If services 
control-flow dependencies has these native functions, the Solveing of services will 
stop.

Related work
----

+ [natural/java2python](https://github.com/natural/java2python) :tested, but no consider some situation. And
it can't pass its test cases.
+ [thoka/java2python](https://github.com/thoka/java2python)

Dependencies
----

+ [plyj](https://github.com/musiKk/plyj)
