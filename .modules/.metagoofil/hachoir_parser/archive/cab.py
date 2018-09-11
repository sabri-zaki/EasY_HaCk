"""
Microsoft Cabinet (CAB) archive.

Author: Victor Stinner, Robert Xiao
Creation date: 31 january 2007

- Microsoft Cabinet SDK
  http://msdn2.microsoft.com/en-us/library/ms974336.aspx
"""
from __future__ import absolute_import
from hachoir_parser import Parser
from hachoir_core.field import (FieldSet, Enum,
    CString, String,
    UInt8, UInt16, UInt32, Bit, Bits, PaddingBits, NullBits,
    DateTimeMSDOS32, RawBytes)
from hachoir_core.text_handler import textHandler, hexadecimal, filesizeHandler
from hachoir_core.endian import LITTLE_ENDIAN
from hachoir_core.tools import paddingSize
from hachoir_core.stream import StringInputStream
from hachoir_parser.archive.lzx import LZXStream, lzx_decompress
from hachoir_parser.archive.zlib import DeflateBlock

MAX_NB_FOLDER = 30

COMPRESSION_NONE = 0
COMPRESSION_NAME = {
    0: "Uncompressed",
    1: "Deflate",
    2: "Quantum",
    3: "LZX",
}

class Folder(FieldSet):
    def createFields(self):
        yield UInt32(self, "offset", "Offset to data (from file start)")
        yield UInt16(self, "data_blocks", "Number of data blocks which are in this cabinet")
        yield Enum(Bits(self, "compr_method", 4, "Compression method"), COMPRESSION_NAME)
        if self["compr_method"].value in [2, 3]: # Quantum or LZX use compression level
            yield PaddingBits(self, "padding[]", 4)
            yield Bits(self, "compr_level", 5, "Compression level")
            yield PaddingBits(self, "padding[]", 3)
        else:
            yield PaddingBits(self, "padding[]", 12)
        if self["../flags/has_reserved"].value and self["../reserved_folder_size"].value:
            yield RawBytes(self, "reserved_folder", self["../reserved_folder_size"].value, "Per-folder reserved area")

    def createDescription(self):
        text= "Folder: compression %s" % self["compr_method"].display
        if self["compr_method"].value in [2, 3]: # Quantum or LZX use compression level
            text += " (level %u: window size %u)" % (self["compr_level"].value, 2**self["compr_level"].value)
        return text

class CabFileAttributes(FieldSet):
    def createFields(self):
        yield Bit(self, "readonly")
        yield Bit(self, "hidden")
        yield Bit(self, "system")
        yield Bits(self, "reserved[]", 2)
        yield Bit(self, "archive", "Has the file been modified since the last backup?")
        yield Bit(self, "exec", "Run file after extraction?")
        yield Bit(self, "name_is_utf", "Is the filename using UTF-8?")
        yield Bits(self, "reserved[]", 8)

class File(FieldSet):
    def createFields(self):
        yield filesizeHandler(UInt32(self, "filesize", "Uncompressed file size"))
        yield UInt32(self, "folder_offset", "File offset in uncompressed folder")
        yield Enum(UInt16(self, "folder_index", "Containing folder ID (index)"), {
            0xFFFD:"Folder continued from previous cabinet (real folder ID = 0)",
            0xFFFE:"Folder continued to next cabinet (real folder ID = %i)" % (self["../nb_folder"].value - 1),
            0xFFFF:"Folder spanning previous, current and next cabinets (real folder ID = 0)"})
        yield DateTimeMSDOS32(self, "timestamp")
        yield CabFileAttributes(self, "attributes")
        if self["attributes/name_is_utf"].value:
            yield CString(self, "filename", charset="UTF-8")
        else:
            yield CString(self, "filename", charset="ASCII")

    def createDescription(self):
        return "File %s (%s)" % (
            self["filename"].display, self["filesize"].display)

class Flags(FieldSet):
    static_size = 16
    def createFields(self):
        yield Bit(self, "has_previous")
        yield Bit(self, "has_next")
        yield Bit(self, "has_reserved")
        yield NullBits(self, "padding", 13)

class FragmentGroup:
    def __init__(self, parser):
        self.items = []
        self.parser = parser
        self.args = {}

    def add(self, item):
        self.items.append(item)

    def createInputStream(self):
        # FIXME: Use lazy stream creation
        data = []
        for item in self.items:
            data.append( item["rawdata"].value )
        data = "".join(data)

        # FIXME: Use smarter code to send arguments
        self.args["compr_level"] = self.items[0].parent.parent.folder["compr_level"].value
        tags = {"class": self.parser, "args": self.args}
        tags = tags.iteritems()
        return StringInputStream(data, "<fragment group>", tags=tags)

class CustomFragment(FieldSet):
    def __init__(self, parent, name, size, parser, description=None, group=None):
        FieldSet.__init__(self, parent, name, description, size=size)
        if not group:
            group = FragmentGroup(parser)
        self.field_size = size
        self.group = group
        self.group.add(self)

    def createFields(self):
        yield RawBytes(self, "rawdata", self.field_size//8)

    def _createInputStream(self, **args):
        return self.group.createInputStream()

class DataBlock(FieldSet):
    def __init__(self, *args, **kwargs):
        FieldSet.__init__(self, *args, **kwargs)
        size = (self["size"].value + 8) * 8 # +8 for header values
        if self["/flags/has_reserved"].value:
            size += self["/reserved_data_size"].value * 8
        self._size = size

    def createFields(self):
        yield textHandler(UInt32(self, "crc32"), hexadecimal)
        yield UInt16(self, "size")
        yield UInt16(self, "uncompressed_size", "If this is 0, this block is continued in a subsequent cabinet")
        if self["/flags/has_reserved"].value and self["/reserved_data_size"].value:
            yield RawBytes(self, "reserved_data", self["/reserved_data_size"].value, "Per-datablock reserved area")
        compr_method = self.parent.folder["compr_method"].value
        if compr_method == 0: # Uncompressed
            yield RawBytes(self, "data", self["size"].value, "Folder Data")
            self.parent.uncompressed_data += self["data"].value
        elif compr_method == 1: # MSZIP
            yield String(self, "mszip_signature", 2, "MSZIP Signature (CK)")
            yield DeflateBlock(self, "deflate_block", self.parent.uncompressed_data)
            padding = paddingSize(self.current_size, 8)
            if padding:
                yield PaddingBits(self, "padding[]", padding)
            self.parent.uncompressed_data = self["deflate_block"].uncomp_data
        elif compr_method == 2: # Quantum
            yield RawBytes(self, "compr_data", self["size"].value, "Compressed Folder Data")
        elif compr_method == 3: # LZX
            group = getattr(self.parent.folder, "lzx_group", None)
            field = CustomFragment(self, "data", self["size"].value*8, LZXStream, "LZX data fragment", group)
            self.parent.folder.lzx_group = field.group
            yield field

class FolderParser(Parser):
    endian = LITTLE_ENDIAN
    def createFields(self):
        for file in sorted(self.files, key=lambda x:x["folder_offset"].value):
            padding = self.seekByte(file["folder_offset"].value)
            if padding:
                yield padding
            yield RawBytes(self, "file[]", file["filesize"].value, file.description)

class FolderData(FieldSet):
    def __init__(self, parent, name, folder, files, *args, **kwargs):
        FieldSet.__init__(self, parent, name, *args, **kwargs)
        def createInputStream(cis, source=None, **args):
            stream = cis(source=source)
            tags = args.setdefault("tags",[])
            tags.extend(stream.tags)
            tags.append(( "class", FolderParser ))
            tags.append(( "args", {'files': files} ))
            for unused in self:
                pass
            if folder["compr_method"].value == 3: # LZX
                self.uncompressed_data = lzx_decompress(self["block[0]/data"].getSubIStream(), folder["compr_level"].value)
            return StringInputStream(self.uncompressed_data, source=source, **args)
        self.setSubIStream(createInputStream)
        self.files = files
        self.folder = folder # Folder fieldset

    def createFields(self):
        self.uncompressed_data = ""
        for index in xrange(self.folder["data_blocks"].value):
            block = DataBlock(self, "block[]")
            for i in block:
                pass
            yield block

class CabFile(Parser):
    endian = LITTLE_ENDIAN
    MAGIC = "MSCF"
    PARSER_TAGS = {
        "id": "cab",
        "category": "archive",
        "file_ext": ("cab",),
        "mime": (u"application/vnd.ms-cab-compressed",),
        "magic": ((MAGIC, 0),),
        "min_size": 1*8, # header + file entry
        "description": "Microsoft Cabinet archive"
    }

    def validate(self):
        if self.stream.readBytes(0, 4) != self.MAGIC:
            return "Invalid magic"
        if self["major_version"].value != 1 or self["minor_version"].value != 3:
            return "Unknown version (%i.%i)" % (self["major_version"].value, self["minor_version"].value)
        if not (1 <= self["nb_folder"].value <= MAX_NB_FOLDER):
            return "Invalid number of folder (%s)" % self["nb_folder"].value
        return True

    def createFields(self):
        yield String(self, "magic", 4, "Magic (MSCF)", charset="ASCII")
        yield textHandler(UInt32(self, "hdr_checksum", "Header checksum (0 if not used)"), hexadecimal)
        yield filesizeHandler(UInt32(self, "filesize", "Cabinet file size"))
        yield textHandler(UInt32(self, "fld_checksum", "Folders checksum (0 if not used)"), hexadecimal)
        yield UInt32(self, "off_file", "Offset of first file")
        yield textHandler(UInt32(self, "files_checksum", "Files checksum (0 if not used)"), hexadecimal)
        yield UInt8(self, "minor_version", "Minor version (should be 3)")
        yield UInt8(self, "major_version", "Major version (should be 1)")
        yield UInt16(self, "nb_folder", "Number of folders")
        yield UInt16(self, "nb_files", "Number of files")
        yield Flags(self, "flags")
        yield UInt16(self, "setid")
        yield UInt16(self, "cabinet_serial", "Zero-based cabinet number")

        if self["flags/has_reserved"].value:
            yield UInt16(self, "reserved_header_size", "Size of per-cabinet reserved area")
            yield UInt8(self, "reserved_folder_size", "Size of per-folder reserved area")
            yield UInt8(self, "reserved_data_size", "Size of per-datablock reserved area")
            if self["reserved_header_size"].value:
                yield RawBytes(self, "reserved_header", self["reserved_header_size"].value, "Per-cabinet reserved area")
        if self["flags/has_previous"].value:
            yield CString(self, "previous_cabinet", "File name of previous cabinet", charset="ASCII")
            yield CString(self, "previous_disk", "Description of disk/media on which previous cabinet resides", charset="ASCII")
        if self["flags/has_next"].value:
            yield CString(self, "next_cabinet", "File name of next cabinet", charset="ASCII")
            yield CString(self, "next_disk", "Description of disk/media on which next cabinet resides", charset="ASCII")

        folders = []
        files = []
        for index in xrange(self["nb_folder"].value):
            folder = Folder(self, "folder[]")
            yield folder
            folders.append(folder)
        for index in xrange(self["nb_files"].value):
            file = File(self, "file[]")
            yield file
            files.append(file)

        folders = sorted(enumerate(folders), key=lambda x:x[1]["offset"].value)

        for i in xrange(len(folders)):
            index, folder = folders[i]
            padding = self.seekByte(folder["offset"].value)
            if padding:
                yield padding
            files = []
            for file in files:
                if file["folder_index"].value == index:
                    files.append(file)
            if i+1 == len(folders):
                size = (self.size // 8) - folder["offset"].value
            else:
                size = (folders[i+1][1]["offset"].value) - folder["offset"].value
            yield FolderData(self, "folder_data[%i]" % index, folder, files, size=size*8)

        end = self.seekBit(self.size, "endraw")
        if end:
            yield end

    def createContentSize(self):
        return self["filesize"].value * 8

