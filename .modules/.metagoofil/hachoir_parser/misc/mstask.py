"""
ms task/job file parser

Author: Jeff Bryner
Creation date: 2010-11
References: 
http://msdn.microsoft.com/en-us/library/cc248286%28v=PROT.13%29.aspx
http://msdn.microsoft.com/en-us/library/cc248287%28v=PROT.13%29.aspx
http://technet.microsoft.com/en-us/library/bb490996.aspx
"""


from hachoir_parser import Parser
from hachoir_core.field import (FieldSet, RootSeekableFieldSet,
    CString, String, PascalString16,
    UInt32, UInt16, UInt8,
    Bit, Bits, PaddingBits,
    TimestampWin64, DateTimeMSDOS32,
    NullBytes, PaddingBytes, RawBits, RawBytes, Enum)
from hachoir_core.endian import LITTLE_ENDIAN, BIG_ENDIAN
from hachoir_core.text_handler import textHandler, hexadecimal
from hachoir_parser.common.win32 import PascalStringWin16, GUID
from hachoir_parser.common.msdos import MSDOSFileAttr16, MSDOSFileAttr32
from hachoir_core.text_handler import filesizeHandler

class TaskTrigger(FieldSet):
    TRIGGER_TYPE = {
        0x00000000: "ONCE",
        0x00000001: "DAILY",
        0x00000002: "WEEKLY",
        0x00000003: "MONTHLYDATE",
        0x00000004: "MONTHLYDOW",
        0x00000005: "EVENT_ON_IDLE",
        0x00000006: "EVENT_AT_SYSTEMSTART",
        0x00000007: "EVENT_AT_LOGON"
    }

    def __init__(self, *args, **kwargs):
        FieldSet.__init__(self, *args, **kwargs)
        self._size = self["TriggerSize"].value * 8

    def createFields(self):
        yield UInt16(self, "TriggerSize")
        yield UInt16(self, "Reserved[]")
        yield UInt16(self, "BeginYear")
        yield UInt16(self, "BeginMonth")
        yield UInt16(self, "BeginDay")
        yield UInt16(self, "EndYear")
        yield UInt16(self, "EndMonth")
        yield UInt16(self, "EndDay")
        yield UInt16(self, "StartHour")
        yield UInt16(self, "StartMinute")
        yield UInt32(self, "MinutesDuration")
        yield UInt32(self, "MinutesInterval","Time period between repeated trigger firings.")
        yield Bit(self, "HasEndDate","Can task stop at some point in time?")
        yield Bit(self, "KillAtDurationEnd","Can task be stopped at the end of the repetition period?")
        yield Bit(self, "TriggerDisabled","Is this trigger disabled?")
        yield RawBits(self, "Unused[]", 29)
        yield Enum(UInt32(self, "TriggerType"),self.TRIGGER_TYPE)
        yield UInt16(self, "TriggerSpecific0")
        yield UInt16(self, "TriggerSpecific1")
        yield UInt16(self, "TriggerSpecific2")
        yield UInt16(self, "Padding")
        yield UInt16(self, "Reserved[]")
        yield UInt16(self, "Reserved[]")

class MSTaskFile(Parser, RootSeekableFieldSet):
    PARSER_TAGS = {
        "id": "mstask",
        "category": "misc",    # "archive", "audio", "container", ...
        "file_ext": ("job",), # TODO: Example ("bmp",) to parse the file "image.bmp"
        "min_size": 100,         # TODO: Minimum file size (x bits, or x*8 in bytes)
        "description": ".job 'at' file parser from ms windows", # TODO: Example: "A bitmap picture",
    }

    endian = LITTLE_ENDIAN

    PRODUCT_VERSION = {
        0x0400: "Windows NT 4.0",
        0x0500: "Windows 2000",
        0x0501: "Windows XP",
        0x0600: "Windows Vista",
        0x0601: "Windows 7"
    }

    TASK_STATUS = {
        0x00041300: "Task Ready",
        0x00041301: "Task running",
        0x00041302: "Task disabled",
        0x00041303: "Task has not run",
        0x00041304: "Task has no more runs",
        0x00041305: "Task not scheduled",
        0x00041306: "Task terminated",
        0x00041307: "Task has no valid triggers",
        0x00041308: "Task contains only event triggers that do not have set run times",
        0x00041309: "Task trigger not found",
        0x0004130A: "One or more of the properties that are required to run this task have not been set.",
        0x0004130B: "There is no running instance of the task",
        0x0004130C: "Task Schedule Remoting Protocol service is not installed",
        0x0004130D: "Task object cannot be opened",
        0x0004130E: "Task object is invalid",
        0x0004130F: "No Account information could be found in Task Scheduler Remoting Protocol security database for the task indicated."
    }

    def validate(self):
        # The MAGIC for a task file is the windows version that created it
        # http://msdn.microsoft.com/en-us/library/2d1fbbab-fe6c-4ae5-bdf5-41dc526b2439%28v=PROT.13%29#id11
        if self['WindowsVersion'].value not in self.PRODUCT_VERSION:
            return "Invalid Product Version Field"
        return True

    def createFields(self):
        yield Enum(UInt16(self, "WindowsVersion"), self.PRODUCT_VERSION)
        yield UInt16(self, "FileVersion")
        yield GUID(self, "JobUUID")
        yield UInt16(self, "AppNameOffset", "App Name Length Offset")
        yield UInt16(self, "TriggerOffset", "Contains the offset in bytes within the .JOB file where the task triggers are located.")
        yield UInt16(self, "ErrorRetryCount", "Contains the number of execute attempts that are attempted for the task if the task fails to start.")
        yield UInt16(self, "ErrorRetryInterval", "Contains the interval, in minutes, between successive retries")
        yield UInt16(self, "IdleDeadline", "Contains a maximum time in minutes to wait for the machine to become idle for Idle Wait minutes.")
        yield UInt16(self, "IdleWait", "Contains a value in minutes. The machine remains idle for this many minutes before it runs the task")
        yield UInt32(self, "Priority")
        yield UInt32(self, "MaxRunTime", "Maximum run time in milliseconds")
        yield UInt32(self, "ExitCode", "This contains the exit code of the executed task upon the completion of that task.")
        yield Enum(UInt32(self, "Status"), self.TASK_STATUS)
        yield Bit(self, "Interactive", "Can Task interact with user?")
        yield Bit(self, "DeleteWhenDone", "Remove the task file when done?")
        yield Bit(self, "Disabled", "Is Task disabled?")
        yield Bit(self, "StartOnlyIfIdle", "Task begins only if computer is not in use at the scheduled time")
        yield Bit(self, "KillOnIdleEnd", "Kill task if user input is detected, terminating idle state?")
        yield Bit(self, "DontStartIfOnBatteries")
        yield Bit(self, "KillIfGoingOnBatteries")
        yield Bit(self, "RunOnlyIfDocked")
        yield Bit(self, "HiddenTask")
        yield Bit(self, "RunIfConnectedToInternet")
        yield Bit(self, "RestartOnIdleResume")
        yield Bit(self, "SystemRequired", "Can task cause system to resume or awaken if system is sleeping?")
        yield Bit(self, "OnlyIfUserLoggedOn")
        yield Bit(self, "ApplicationNameExists", "Does task have an application name defined?")
        yield Bit(self, "Unused[]")
        yield Bit(self, "Unused[]")
        yield RawBytes(self, "flags", 2)
        yield UInt16(self, "LastRunYear")
        yield UInt16(self, "LastRunMonth")
        yield UInt16(self, "LastRunWeekday", "Sunday=0,Saturday=6")
        yield UInt16(self, "LastRunDay")
        yield UInt16(self, "LastRunHour")
        yield UInt16(self, "LastRunMinute")
        yield UInt16(self, "LastRunSecond")
        yield UInt16(self, "LastRunMillisecond")
        yield UInt16(self, "RunningInstanceCount")
        yield PascalStringWin16(self, "AppNameLength", strip='\0')
        yield PascalStringWin16(self, "Parameters", strip='\0')
        yield PascalStringWin16(self, "WorkingDirectory", strip='\0')
        yield PascalStringWin16(self, "Author", strip='\0')
        yield PascalStringWin16(self, "Comment", strip='\0')

        yield UInt16(self, "UserDataSize")
        #todo: read optional userdata
        yield UInt16(self, "ReservedDataSize")
        if self["ReservedDataSize"].value==8:
            yield Enum(UInt32(self, "StartError", "contains the HRESULT error from the most recent attempt to start the task"), self.TASK_STATUS)
            yield UInt32(self, "TaskFlags")
        elif self["ReservedDataSize"].value:
            yield RawBytes(self, "Reserved", self["ReservedDataSize"].value)
        yield UInt16(self, "TriggerCount", "size of the array of triggers")
        for i in xrange(self["TriggerCount"].value):
            yield TaskTrigger(self, "Trigger[]")
