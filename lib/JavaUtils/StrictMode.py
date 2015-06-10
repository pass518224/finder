from InstrumentClass import *
import ApplicationErrorReport
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
