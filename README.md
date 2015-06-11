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

Transaction features
----

### Needed Packages to be included

Python need to include/import files only when it want to create **instance** or **extends (implements)**.

Not like java. Java need the exactly size of each class, so if we use a class, even declare a type pointer,
we have to import the source. This feature make including been very difficult. While translating into Python
code, only we have to consider is insance and extends.

Transaction problems
----

### Java built-in packages

Java have many built-in packages, we need a standard support of these libraries.

### Unary, assignment in condition(while, for, if, elif) or array accessing

In c/c++ coding. But python dont have these features.
`a++`, `if (i++ > 0)` are not supported in python.

multi-times assignment are also not supported

    int a = b = 100

Instead of previous case, we use:

    b = 100
    int a = b

So we need to decouple the multi-times assignment in python code.

And, Python doesn't support `i++` or `++i` type unary operator.
Instead of this `i += 1`.

The main problem is java style conditions

    while (((event = in.next()) != XmlPullParser.END_DOCUMENT)) {
        if (event == XmlPullParser.START_TAG) {
            name = in.getName();
        }
    }

This case have an assignment then comparation. 
Put an assignment in condition is invalid,

### Extend outer class

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

### Anonymous Class

java has anonymous class that let you override the sub-part without explicit declaring a new one
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

### Function overloading

Java have a feature of function overloadin. 
The caller will call the corresponding function base on passed parameters. 
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

Related work
----

+ [natural/java2python](https://github.com/natural/java2python) :tested, but no consider some situation. And
it can't pass its test cases.
+ [thoka/java2python](https://github.com/thoka/java2python)

Dependencies
----

+ [plyj](https://github.com/musiKk/plyj)
