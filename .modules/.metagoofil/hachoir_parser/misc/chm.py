"""
InfoTech Storage Format (ITSF) parser, used by Microsoft's HTML Help (.chm)

Document:
- Microsoft's HTML Help (.chm) format
  http://www.wotsit.org (search "chm")
- chmlib library
  http://www.jedrea.com/chmlib/
- Unofficial CHM Spec
  http://savannah.nongnu.org/projects/chmspec
- Microsoft's HTML Help (.chm) format
  http://www.speakeasy.org/~russotto/chm/chmformat.html

Author: Victor Stinner
Creation date: 2007-03-04
"""

from hachoir_core.field import (Field, FieldSet, ParserError, RootSeekableFieldSet,
    Int32, UInt16, UInt32, UInt64,
    RawBytes, PaddingBytes,
    Enum, String)
from hachoir_core.endian import LITTLE_ENDIAN
from hachoir_parser import HachoirParser
from hachoir_parser.common.win32 import GUID
from hachoir_parser.common.win32_lang_id import LANGUAGE_ID
from hachoir_core.text_handler import textHandler, hexadecimal, filesizeHandler

class CWord(Field):
    """
    Compressed double-word
    """
    def __init__(self, parent, name, description=None):
        Field.__init__(self, parent, name, 8, description)

        endian = self._parent.endian
        stream = self._parent.stream
        addr = self.absolute_address

        value = 0
        byte = stream.readBits(addr, 8, endian)
        while byte & 0x80:
            value <<= 7
            value += (byte & 0x7f)
            self._size += 8
            if 64 < self._size:
                raise ParserError("CHM: CWord is limited to 64 bits")
            addr += 8
            byte = stream.readBits(addr, 8, endian)
        value <<= 7
        value += byte
        self.createValue = lambda: value

class Filesize_Header(FieldSet):
    def createFields(self):
        yield textHandler(UInt32(self, "unknown[]", "0x01FE"), hexadecimal)
        yield textHandler(UInt32(self, "unknown[]", "0x0"), hexadecimal)
        yield filesizeHandler(UInt64(self, "file_size"))
        yield textHandler(UInt32(self, "unknown[]", "0x0"), hexadecimal)
        yield textHandler(UInt32(self, "unknown[]", "0x0"), hexadecimal)

class ITSP(FieldSet):
    def __init__(self, *args):
        FieldSet.__init__(self, *args)
        self._size = self["size"].value * 8

    def createFields(self):
        yield String(self, "magic", 4, "ITSP", charset="ASCII")
        yield UInt32(self, "version", "Version (=1)")
        yield filesizeHandler(UInt32(self, "size", "Length (in bytes) of the directory header (84)"))
        yield UInt32(self, "unknown[]", "(=10)")
        yield filesizeHandler(UInt32(self, "block_size", "Directory block size"))
        yield UInt32(self, "density", "Density of quickref section, usually 2")
        yield UInt32(self, "index_depth", "Depth of the index tree")
        yield Int32(self, "nb_dir", "Chunk number of root index chunk")
        yield UInt32(self, "first_pmgl", "Chunk number of first PMGL (listing) chunk")
        yield UInt32(self, "last_pmgl", "Chunk number of last PMGL (listing) chunk")
        yield Int32(self, "unknown[]", "-1")
        yield UInt32(self, "nb_dir_chunk", "Number of directory chunks (total)")
        yield Enum(UInt32(self, "lang_id", "Windows language ID"), LANGUAGE_ID)
        yield GUID(self, "system_uuid", "{5D02926A-212E-11D0-9DF9-00A0C922E6EC}")
        yield filesizeHandler(UInt32(self, "size2", "Same value than size"))
        yield Int32(self, "unknown[]", "-1")
        yield Int32(self, "unknown[]", "-1")
        yield Int32(self, "unknown[]", "-1")

class ITSF(FieldSet):
    def createFields(self):
        yield String(self, "magic", 4, "ITSF", charset="ASCII")
        yield UInt32(self, "version")
        yield UInt32(self, "header_size", "Total header length (in bytes)")
        yield UInt32(self, "one")
        yield UInt32(self, "last_modified", "Lower 32 bits of the time expressed in units of 0.1 us")
        yield Enum(UInt32(self, "lang_id", "Windows Language ID"), LANGUAGE_ID)
        yield GUID(self, "dir_uuid", "{7C01FD10-7BAA-11D0-9E0C-00A0-C922-E6EC}")
        yield GUID(self, "stream_uuid", "{7C01FD11-7BAA-11D0-9E0C-00A0-C922-E6EC}")
        yield UInt64(self, "filesize_offset")
        yield filesizeHandler(UInt64(self, "filesize_len"))
        yield UInt64(self, "dir_offset")
        yield filesizeHandler(UInt64(self, "dir_len"))
        if 3 <= self["version"].value:
            yield UInt64(self, "data_offset")

class PMGL_Entry(FieldSet):
    def createFields(self):
        yield CWord(self, "name_len")
        yield String(self, "name", self["name_len"].value, charset="UTF-8")
        yield CWord(self, "section", "Section number that the entry data is in.")
        yield CWord(self, "start", "Start offset of the data")
        yield filesizeHandler(CWord(self, "length", "Length of the data"))

    def createDescription(self):
        return "%s (%s)" % (self["name"].value, self["length"].display)

class PMGL(FieldSet):
    def createFields(self):
        # Header
        yield String(self, "magic", 4, "PMGL", charset="ASCII")
        yield filesizeHandler(Int32(self, "free_space",
            "Length of free space and/or quickref area at end of directory chunk"))
        yield Int32(self, "unknown")
        yield Int32(self, "previous", "Chunk number of previous listing chunk")
        yield Int32(self, "next", "Chunk number of previous listing chunk")

        # Entries
        stop = self.size - self["free_space"].value * 8
        entry_count = 0
        while self.current_size < stop:
            yield PMGL_Entry(self, "entry[]")
            entry_count+=1

        # Padding
        quickref_frequency = 1 + (1 << self["/dir/itsp/density"].value)
        num_quickref = (entry_count // quickref_frequency)
        if entry_count % quickref_frequency == 0:
            num_quickref -= 1
        print self.current_size//8, quickref_frequency, num_quickref
        padding = (self["free_space"].value - (num_quickref*2+2))
        if padding:
            yield PaddingBytes(self, "padding", padding)
        for i in range(num_quickref*quickref_frequency, 0, -quickref_frequency):
            yield UInt16(self, "quickref[%i]"%i)
        yield UInt16(self, "entry_count")

class PMGI_Entry(FieldSet):
    def createFields(self):
        yield CWord(self, "name_len")
        yield String(self, "name", self["name_len"].value, charset="UTF-8")
        yield CWord(self, "page")

    def createDescription(self):
        return "%s (page #%u)" % (self["name"].value, self["page"].value)

class PMGI(FieldSet):
    def createFields(self):
        yield String(self, "magic", 4, "PMGI", charset="ASCII")
        yield filesizeHandler(UInt32(self, "free_space",
            "Length of free space and/or quickref area at end of directory chunk"))

        stop = self.size - self["free_space"].value * 8
        while self.current_size < stop:
            yield PMGI_Entry(self, "entry[]")

        padding = (self.size - self.current_size) // 8
        if padding:
            yield PaddingBytes(self, "padding", padding)

class Directory(FieldSet):
    def createFields(self):
        yield ITSP(self, "itsp")
        block_size = self["itsp/block_size"].value * 8

        nb_dir = self["itsp/nb_dir"].value

        if nb_dir < 0:
            nb_dir = 1
        for index in xrange(nb_dir):
            yield PMGL(self, "pmgl[]", size=block_size)

        if self.current_size < self.size:
            yield PMGI(self, "pmgi", size=block_size)

class NameList(FieldSet):
    def createFields(self):
        yield UInt16(self, "length", "Length of name list in 2-byte blocks")
        yield UInt16(self, "count", "Number of entries in name list")
        for index in range(self["count"].value):
            length=UInt16(self, "name_len[]", "Length of name in 2-byte blocks, excluding terminating null")
            yield length
            yield String(self, "name[]", length.value*2+2, charset="UTF-16-LE")

class ControlData(FieldSet):
    def createFields(self):
        yield UInt32(self, "count", "Number of DWORDS in this struct")
        yield String(self, "type", 4, "Type of compression")
        if self["type"].value!='LZXC': return
        yield UInt32(self, "version", "Compression version")
        version=self["version"].value
        if version==1: block='bytes'
        else: block='32KB blocks'
        yield UInt32(self, "reset_interval", "LZX: Reset interval in %s"%block)
        yield UInt32(self, "window_size", "LZX: Window size in %s"%block)
        yield UInt32(self, "cache_size", "LZX: Cache size in %s"%block)
        yield UInt32(self, "unknown[]")

class ResetTable(FieldSet):
    def createFields(self):
        yield UInt32(self, "unknown[]", "Version number?")
        yield UInt32(self, "count", "Number of entries")
        yield UInt32(self, "entry_size", "Size of each entry")
        yield UInt32(self, "header_size", "Size of this header")
        yield UInt64(self, "uncompressed_size")
        yield UInt64(self, "compressed_size")
        yield UInt64(self, "block_size", "Block size in bytes")
        for i in xrange(self["count"].value):
            yield UInt64(self, "block_location[]", "location in compressed data of 1st block boundary in uncompressed data")

class SystemEntry(FieldSet):
    ENTRY_TYPE={0:"HHP: [OPTIONS]: Contents File",
                1:"HHP: [OPTIONS]: Index File",
                2:"HHP: [OPTIONS]: Default Topic",
                3:"HHP: [OPTIONS]: Title",
                4:"File Metadata",
                5:"HHP: [OPTIONS]: Default Window",
                6:"HHP: [OPTIONS]: Compiled file",
                # 7 present only in files with Binary Index; unknown function
                # 8 unknown function
                9: "Version",
                10: "Timestamp",
                # 11 only in Binary TOC files
                12: "Number of Info Types",
                13: "#IDXHDR file",
                # 14 unknown function
                # 15 checksum??
                16:"HHP: [OPTIONS]: Default Font",
    }
    def createFields(self):
        yield Enum(UInt16(self, "type", "Type of entry"),self.ENTRY_TYPE)
        yield UInt16(self, "length", "Length of entry")
        yield RawBytes(self, "data", self["length"].value)
    def createDescription(self):
        return '#SYSTEM Entry, Type %s'%self["type"].display
        
class SystemFile(FieldSet):
    def createFields(self):
        yield UInt32(self, "version", "Either 2 or 3")
        while self.current_size < self.size:
            yield SystemEntry(self, "entry[]")

class ChmFile(HachoirParser, RootSeekableFieldSet):
    MAGIC = "ITSF\3\0\0\0"
    PARSER_TAGS = {
        "id": "chm",
        "category": "misc",
        "file_ext": ("chm",),
        "min_size": 4*8,
        "magic": ((MAGIC, 0),),
        "description": "Microsoft's HTML Help (.chm)",
    }
    endian = LITTLE_ENDIAN

    def __init__(self, stream, **args):
        RootSeekableFieldSet.__init__(self, None, "root", stream, None, stream.askSize(self))
        HachoirParser.__init__(self, stream, **args)

    def validate(self):
        if self.stream.readBytes(0, len(self.MAGIC)) != self.MAGIC:
            return "Invalid magic"
        return True

    def createFields(self):
        yield ITSF(self, "itsf")
        yield Filesize_Header(self, "file_size", size=self["itsf/filesize_len"].value*8)

        self.seekByte(self["itsf/dir_offset"].value)
        directory=Directory(self, "dir", size=self["itsf/dir_len"].value*8)
        yield directory

        otherentries = {}
        for pmgl in directory.array("pmgl"):
            for entry in pmgl.array("entry"):
                if entry["section"].value != 0:
                    otherentries.setdefault(entry["section"].value,[]).append(entry)
                    continue
                if entry["length"].value == 0:
                    continue
                self.seekByte(self["itsf/data_offset"].value+entry["start"].value)
                name = entry["name"].value
                if name == "::DataSpace/NameList":
                    yield NameList(self, "name_list")
                elif name.startswith('::DataSpace/Storage/'):
                    sectname = str(name.split('/')[2])
                    if name.endswith('/SpanInfo'):
                        yield UInt64(self, "%s_spaninfo"%sectname, "Size of uncompressed data in the %s section"%sectname)
                    elif name.endswith('/ControlData'):
                        yield ControlData(self, "%s_controldata"%sectname, "Data about the compression scheme", size=entry["length"].value*8)
                    elif name.endswith('/Transform/List'):
                        yield String(self, "%s_transform_list"%sectname, 38, description="Transform/List element", charset="UTF-16-LE")
                    elif name.endswith('/Transform/{7FC28940-9D31-11D0-9B27-00A0C91E9C7C}/InstanceData/ResetTable'):
                        yield ResetTable(self, "%s_reset_table"%sectname, "LZX Reset Table", size=entry["length"].value*8)
                    elif name.endswith('/Content'):
                        # eventually, a LZX wrapper will appear here, we hope!
                        yield RawBytes(self, "%s_content"%sectname, entry["length"].value, "Content for the %s section"%sectname)
                    else:
                        yield RawBytes(self, "entry_data[]", entry["length"].value, name)
                elif name=="/#SYSTEM":
                    yield SystemFile(self, "system_file", size=entry["length"].value*8)
                else:
                    yield RawBytes(self, "entry_data[]", entry["length"].value, name)

    def getFile(self, filename):
        page=0
        if 'pmgi' in self['/dir']:
            for entry in self['/dir/pmgi'].array('entry'):
                if entry['name'].value <= filename:
                    page=entry['page'].value
        pmgl=self['/dir/pmgl[%i]'%page]
        for entry in pmgl.array('entry'):
            if entry['name'].value == filename:
                return entry
        raise ParserError("File '%s' not found!"%filename)

    def createContentSize(self):
        return self["file_size/file_size"].value * 8

