"""
ELF (Unix/BSD executable file format) parser.

Author: Victor Stinner, Robert Xiao
Creation date: 08 may 2006
"""

from hachoir_parser import HachoirParser
from hachoir_core.field import (RootSeekableFieldSet, FieldSet, ParserError, Bit, NullBits, RawBits,
    UInt8, UInt16, UInt32, UInt64, Enum,
    String, RawBytes, Bytes)
from hachoir_core.text_handler import textHandler, hexadecimal
from hachoir_core.endian import LITTLE_ENDIAN, BIG_ENDIAN

class ElfHeader(FieldSet):
    LITTLE_ENDIAN_ID = 1
    BIG_ENDIAN_ID = 2
    MACHINE_NAME = {
        # e_machine, EM_ defines
        0: u"No machine",
        1: u"AT&T WE 32100",
        2: u"SPARC",
        3: u"Intel 80386",
        4: u"Motorola 68000",
        5: u"Motorola 88000",
        6: u"Intel 80486",
        7: u"Intel 80860",
        8: u"MIPS I Architecture",
        9: u"Amdahl UTS on System/370",
        10: u"MIPS RS3000 Little-endian",
        11: u"IBM RS/6000 XXX reserved",
        15: u"Hewlett-Packard PA-RISC",
        16: u"NCube XXX reserved",
        17: u"Fujitsu VPP500",
        18: u"Enhanced instruction set SPARC",
        19: u"Intel 80960",
        20: u"PowerPC 32-bit",
        21: u"PowerPC 64-bit",
        36: u"NEC V800",
        37: u"Fujitsu FR20",
        38: u"TRW RH-32",
        39: u"Motorola RCE",
        40: u"Advanced RISC Machines (ARM)",
        41: u"DIGITAL Alpha",
        42: u"Hitachi Super-H",
        43: u"SPARC Version 9",
        44: u"Siemens Tricore",
        45: u"Argonaut RISC Core",
        46: u"Hitachi H8/300",
        47: u"Hitachi H8/300H",
        48: u"Hitachi H8S",
        49: u"Hitachi H8/500",
        50: u"Intel Merced (IA-64) Processor",
        51: u"Stanford MIPS-X",
        52: u"Motorola Coldfire",
        53: u"Motorola MC68HC12",
        62: u"Advanced Micro Devices x86-64",
        75: u"DIGITAL VAX",
        36902: u"used by NetBSD/alpha; obsolete",
    }
    CLASS_NAME = {
        # e_ident[EI_CLASS], ELFCLASS defines
        1: u"32 bits",
        2: u"64 bits"
    }
    TYPE_NAME = {
        # e_type, ET_ defines
             0: u"No file type",
             1: u"Relocatable file",
             2: u"Executable file",
             3: u"Shared object file",
             4: u"Core file",
        0xFF00: u"Processor-specific (0xFF00)",
        0xFFFF: u"Processor-specific (0xFFFF)",
    }
    OSABI_NAME = {
        # e_ident[EI_OSABI], ELFOSABI_ defines
        0: u"UNIX System V ABI",
        1: u"HP-UX operating system",
        2: u"NetBSD",
        3: u"GNU/Linux",
        4: u"GNU/Hurd",
        5: u"86Open common IA32 ABI",
        6: u"Solaris",
        7: u"Monterey",
        8: u"IRIX",
        9: u"FreeBSD",
        10: u"TRU64 UNIX",
        11: u"Novell Modesto",
        12: u"OpenBSD",
        97: u"ARM",
        255: u"Standalone (embedded) application",
    }
    ENDIAN_NAME = {
        # e_ident[EI_DATA], ELFDATA defines
        LITTLE_ENDIAN_ID: "Little endian",
        BIG_ENDIAN_ID: "Big endian",
    }

    def createFields(self):
        yield Bytes(self, "signature", 4, r'ELF signature ("\x7fELF")')
        yield Enum(UInt8(self, "class", "Class"), self.CLASS_NAME)
        if self["class"].value == 1:
            ElfLongWord = UInt32
        else:
            ElfLongWord = UInt64
        yield Enum(UInt8(self, "endian", "Endian"), self.ENDIAN_NAME)
        yield UInt8(self, "file_version", "File version")
        yield Enum(UInt8(self, "osabi_ident", "OS/syscall ABI identification"), self.OSABI_NAME)
        yield UInt8(self, "abi_version", "syscall ABI version")
        yield String(self, "pad", 7, "Pad")
        
        yield Enum(UInt16(self, "type", "File type"), self.TYPE_NAME)
        yield Enum(UInt16(self, "machine", "Machine type"), self.MACHINE_NAME)
        yield UInt32(self, "version", "ELF format version")
        yield textHandler(ElfLongWord(self, "entry", "Entry point"), hexadecimal)
        yield ElfLongWord(self, "phoff", "Program header file offset")
        yield ElfLongWord(self, "shoff", "Section header file offset")
        yield UInt32(self, "flags", "Architecture-specific flags")
        yield UInt16(self, "ehsize", "Elf header size (this header)")
        yield UInt16(self, "phentsize", "Program header entry size")
        yield UInt16(self, "phnum", "Program header entry count")
        yield UInt16(self, "shentsize", "Section header entry size")
        yield UInt16(self, "shnum", "Section header entry count")
        yield UInt16(self, "shstrndx", "Section header string table index")

    def isValid(self):
        if self["signature"].value != "\x7FELF":
            return "Wrong ELF signature"
        if self["class"].value not in self.CLASS_NAME:
            return "Unknown class"
        if self["endian"].value not in self.ENDIAN_NAME:
            return "Unknown endian (%s)" % self["endian"].value
        return ""

class SectionFlags(FieldSet):
    def createFields(self):
        if self.root.endian == BIG_ENDIAN:
            if self.root.is64bit:
                yield RawBits(self, "reserved[]", 32)
            yield RawBits(self, "processor_specific", 4, "Processor specific flags")
            yield NullBits(self, "reserved[]", 17)
            yield Bit(self, "is_tls", "Section contains TLS data?")
            yield NullBits(self, "reserved[]", 7)
            yield Bit(self, "is_exec", "Section contains executable instructions?")
            yield Bit(self, "is_alloc", "Section occupies memory?")
            yield Bit(self, "is_writable", "Section contains writable data?")
        else:
            yield Bit(self, "is_writable", "Section contains writable data?")
            yield Bit(self, "is_alloc", "Section occupies memory?")
            yield Bit(self, "is_exec", "Section contains executable instructions?")
            yield NullBits(self, "reserved[]", 7)
            yield Bit(self, "is_tls", "Section contains TLS data?")
            yield RawBits(self, "processor_specific", 4, "Processor specific flags")
            yield NullBits(self, "reserved[]", 17)
            if self.root.is64bit:
                yield RawBits(self, "reserved[]", 32)

class SymbolStringTableOffset(UInt32):
    def createDisplay(self):
        section_index = self['/header/shstrndx'].value
        section = self['/section['+str(section_index)+']']
        text = section.value[self.value:]
        return text.split('\0',1)[0]

class SectionHeader32(FieldSet):
    static_size = 40*8
    TYPE_NAME = {
        # sh_type, SHT_ defines
        0: "Inactive",
        1: "Program defined information",
        2: "Symbol table section",
        3: "String table section",
        4: "Relocation section with addends",
        5: "Symbol hash table section",
        6: "Dynamic section",
        7: "Note section",
        8: "Block started by symbol (BSS) or No space section",
        9: "Relocation section without addends",
        10:"Reserved - purpose unknown",
        11:"Dynamic symbol table section",
    }

    def createFields(self):
        yield SymbolStringTableOffset(self, "name", "Section name (index into section header string table)")
        yield Enum(textHandler(UInt32(self, "type", "Section type"), hexadecimal), self.TYPE_NAME)
        yield SectionFlags(self, "flags", "Section flags")
        yield textHandler(UInt32(self, "VMA", "Virtual memory address"), hexadecimal)
        yield textHandler(UInt32(self, "LMA", "Logical memory address (offset in file)"), hexadecimal)
        yield textHandler(UInt32(self, "size", "Section size (bytes)"), hexadecimal)
        yield UInt32(self, "link", "Index of a related section")
        yield UInt32(self, "info", "Type-dependent information")
        yield UInt32(self, "addr_align", "Address alignment (bytes)")
        yield UInt32(self, "entry_size", "Size of each entry in section")

    def createDescription(self):
        return "Section header (name: %s, type: %s)" % \
            (self["name"].display, self["type"].display)

class SectionHeader64(SectionHeader32):
    static_size = 64*8

    def createFields(self):
        yield SymbolStringTableOffset(self, "name", "Section name (index into section header string table)")
        yield Enum(textHandler(UInt32(self, "type", "Section type"), hexadecimal), self.TYPE_NAME)
        yield SectionFlags(self, "flags", "Section flags")
        yield textHandler(UInt64(self, "VMA", "Virtual memory address"), hexadecimal)
        yield textHandler(UInt64(self, "LMA", "Logical memory address (offset in file)"), hexadecimal)
        yield textHandler(UInt64(self, "size", "Section size (bytes)"), hexadecimal)
        yield UInt32(self, "link", "Index of a related section")
        yield UInt32(self, "info", "Type-dependent information")
        yield UInt64(self, "addr_align", "Address alignment (bytes)")
        yield UInt64(self, "entry_size", "Size of each entry in section")

class ProgramFlags(FieldSet):
    static_size = 32
    FLAGS = (('pf_r','readable'),('pf_w','writable'),('pf_x','executable'))

    def createFields(self):
        if self.root.endian == BIG_ENDIAN:
            yield NullBits(self, "padding[]", 29)
            for fld, desc in self.FLAGS:
                yield Bit(self, fld, "Segment is " + desc)
        else:
            for fld, desc in reversed(self.FLAGS):
                yield Bit(self, fld, "Segment is " + desc)
            yield NullBits(self, "padding[]", 29)

    def createDescription(self):
        attribs=[]
        for fld, desc in self.FLAGS:
            if self[fld].value:
                attribs.append(desc)
        return 'Segment is '+', '.join(attribs)

class ProgramHeader32(FieldSet):
    TYPE_NAME = {
        # p_type, PT_ defines
        0: u"Unused program header table entry",
        1: u"Loadable program segment",
        2: u"Dynamic linking information",
        3: u"Program interpreter",
        4: u"Auxiliary information",
        5: u"Reserved, unspecified semantics",
        6: u"Entry for header table itself",
        7: u"Thread Local Storage segment",
        0x70000000: u"MIPS_REGINFO",
    }
    static_size = 32*8

    def createFields(self):
        yield Enum(UInt32(self, "type", "Segment type"), ProgramHeader32.TYPE_NAME)
        yield UInt32(self, "offset", "Offset")
        yield textHandler(UInt32(self, "vaddr", "V. address"), hexadecimal)
        yield textHandler(UInt32(self, "paddr", "P. address"), hexadecimal)
        yield UInt32(self, "file_size", "File size")
        yield UInt32(self, "mem_size", "Memory size")
        yield ProgramFlags(self, "flags")
        yield UInt32(self, "align", "Alignment padding")

    def createDescription(self):
        return "Program Header (%s)" % self["type"].display

class ProgramHeader64(ProgramHeader32):
    static_size = 56*8

    def createFields(self):
        yield Enum(UInt32(self, "type", "Segment type"), ProgramHeader32.TYPE_NAME)
        yield ProgramFlags(self, "flags")
        yield UInt64(self, "offset", "Offset")
        yield textHandler(UInt64(self, "vaddr", "V. address"), hexadecimal)
        yield textHandler(UInt64(self, "paddr", "P. address"), hexadecimal)
        yield UInt64(self, "file_size", "File size")
        yield UInt64(self, "mem_size", "Memory size")
        yield UInt64(self, "align", "Alignment padding")

class ElfFile(HachoirParser, RootSeekableFieldSet):
    MAGIC = "\x7FELF"
    PARSER_TAGS = {
        "id": "elf",
        "category": "program",
        "file_ext": ("so", ""),
        "min_size": 52*8,  # At least one program header
        "mime": (
            u"application/x-executable",
            u"application/x-object",
            u"application/x-sharedlib",
            u"application/x-executable-file",
            u"application/x-coredump"),
        "magic": (("\x7FELF", 0),),
        "description": "ELF Unix/BSD program/library"
    }
    endian = LITTLE_ENDIAN

    def __init__(self, stream, **args):
        RootSeekableFieldSet.__init__(self, None, "root", stream, None, stream.askSize(self))
        HachoirParser.__init__(self, stream, **args)

    def validate(self):
        if self.stream.readBytes(0, len(self.MAGIC)) != self.MAGIC:
            return "Invalid magic"
        err = self["header"].isValid()
        if err:
            return err
        return True

    def createFields(self):
        # Choose the right endian depending on endian specified in header
        if self.stream.readBits(5*8, 8, BIG_ENDIAN) == ElfHeader.BIG_ENDIAN_ID:
            self.endian = BIG_ENDIAN
        else:
            self.endian = LITTLE_ENDIAN

        # Parse header and program headers
        yield ElfHeader(self, "header", "Header")
        self.is64bit = (self["header/class"].value == 2)

        for index in xrange(self["header/phnum"].value):
            if self.is64bit:
                yield ProgramHeader64(self, "prg_header[]")
            else:
                yield ProgramHeader32(self, "prg_header[]")

        self.seekByte(self["header/shoff"].value, relative=False)

        for index in xrange(self["header/shnum"].value):
            if self.is64bit:
                yield SectionHeader64(self, "section_header[]")
            else:
                yield SectionHeader32(self, "section_header[]")
        
        for index in xrange(self["header/shnum"].value):
            field = self["section_header["+str(index)+"]"]
            if field['size'].value != 0:
                self.seekByte(field['LMA'].value, relative=False)
                yield RawBytes(self, "section["+str(index)+"]", field['size'].value)

    def createDescription(self):
        return "ELF Unix/BSD program/library: %s" % (
            self["header/class"].display)

