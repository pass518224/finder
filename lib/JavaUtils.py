def ComponentName(data):
    """/frameworks/base/core/java/android/content/ComponentName.java"""
    mpkg = data.readString()
    mClass = data.readString()

class InstrumentClass(object):
    def __init__(self):
        pass
    
    def __str__(self):
        return self.dump()

    def __repr__(self):
        return self.dump()

    def dump(self):
        line = "Class name : " + self.__class__.__name__
        for mem in [attr for attr in dir(self) if not callable(attr) and not attr.startswith("__")]:
            if  mem == "dump":
                continue
            line += "{0:>12} {1}".format(mem, getattr(self, mem))
        return line

class StrictMode(InstrumentClass):
    class ViolationInfo(InstrumentClass):
        def __init__(self, data):
            self.crashInfo = ApplicationErrorReport.CrashInfo(data)
            self.rawPolicy = data.readInt()
            self.durationMillis        = data.readInt()
            self.violationNumThisLoop  = data.readInt()
            self.numAnimationsRunning  = data.readInt()
            self.violationUptimeMillis = data.readLong()
            self.numInstances          = data.readLong()
            self.broadcastIntentAction = data.readString()
            self.tags                  = data.readStringArray()
            
class ApplicationErrorReport(InstrumentClass):
    class CrashInfo(InstrumentClass):
        def __init__(self, data):
            self.exceptionClassName = data.readString();
            self.exceptionMessage = data.readString();
            self.throwFileName = data.readString();
            self.throwClassName = data.readString();
            self.throwMethodName = data.readString();
            self.throwLineNumber = data.readInt();
            self.stackTrace = data.readString();
