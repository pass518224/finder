from InstrumentClass import *
class CrashInfo(InstrumentClass):
    def __init__(self, data):
        self.exceptionClassName = data.readString();
        self.exceptionMessage = data.readString();
        self.throwFileName = data.readString();
        self.throwClassName = data.readString();
        self.throwMethodName = data.readString();
        self.throwLineNumber = data.readInt();
        self.stackTrace = data.readString();
