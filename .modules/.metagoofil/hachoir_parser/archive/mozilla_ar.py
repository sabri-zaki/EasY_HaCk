"""MAR (Mozilla ARchive) parser

Author: Robert Xiao
Creation date: July 10, 2007

"""

from hachoir_core.endian import BIG_ENDIAN
from hachoir_core.field import (RootSeekableFieldSet, FieldSet,
    String, CString, UInt32, RawBytes)
from hachoir_core.text_handler import displayHandler, filesizeHandler
from hachoir_core.tools import humanUnixAttributes
from hachoir_parser import HachoirParser

class IndexEntry(FieldSet):
    def createFields(self):
        yield UInt32(self, "offset", "Offset in bytes relative to start of archive")
        yield filesizeHandler(UInt32(self, "length", "Length in bytes"))
        yield displayHandler(UInt32(self, "flags"), humanUnixAttributes)
        yield CString(self, "name", "Filename (byte array)")

    def createDescription(self):
        return 'File %s, Size %s, Mode %s'%(
            self["name"].display, self["length"].display, self["flags"].display)

class MozillaArchive(HachoirParser, RootSeekableFieldSet):
    MAGIC = "MAR1"
    PARSER_TAGS = {
        "id": "mozilla_ar",
        "category": "archive",
        "file_ext": ("mar",),
        "min_size": (8+4+13)*8,  # Header, Index Header, 1 Index Entry
        "magic": ((MAGIC, 0),),
        "description": "Mozilla Archive",
    }
    endian = BIG_ENDIAN
    
    def __init__(self, stream, **args):
        RootSeekableFieldSet.__init__(self, None, "root", stream, None, stream.askSize(self))
        HachoirParser.__init__(self, stream, **args)
        
    def validate(self):
        if self.stream.readBytes(0, 4) != self.MAGIC:
            return "Invalid magic"
        return True

    def createFields(self):
        yield String(self, "magic", 4, "File signature (MAR1)", charset="ASCII")
        yield UInt32(self, "index_offset", "Offset to index relative to file start")
        self.seekByte(self["index_offset"].value, False)
        yield UInt32(self, "index_size", "size of index in bytes")
        current_index_size = 0 # bytes
        while current_index_size < self["index_size"].value:
            # plus 4 compensates for index_size
            self.seekByte(self["index_offset"].value + current_index_size + 4, False)
            entry = IndexEntry(self, "index_entry[]")
            yield entry
            current_index_size += entry.size // 8
            self.seekByte(entry["offset"].value, False)
            yield RawBytes(self, "file[]", entry["length"].value)
