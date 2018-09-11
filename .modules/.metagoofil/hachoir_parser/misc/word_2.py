"""
Documents:

* "Microsoft Word for Windows 2.0 Binary Format"
   http://www.wotsit.org/download.asp?f=word2&sc=275927573
"""

from hachoir_core.field import (FieldSet, Enum,
    Bit, Bits,
    UInt8, Int16, UInt16, UInt32, Int32,
    NullBytes, Bytes, RawBytes, PascalString16,
    DateTimeMSDOS32, TimeDateMSDOS32)
from hachoir_core.endian import LITTLE_ENDIAN
from hachoir_parser.misc.ole2_util import OLE2FragmentParser
from hachoir_core.tools import paddingSize
from hachoir_parser.common.win32_lang_id import LANGUAGE_ID
TIMESTAMP = DateTimeMSDOS32

class FC_CB(FieldSet):
    def createFields(self):
        yield Int32(self, "fc", "File Offset")
        yield UInt16(self, "cb", "Byte Count")
    def createValue(self):
        return (self['fc'].value,self['cb'].value)

class FIB(FieldSet):
    def createFields(self):
        yield UInt16(self, "wIdent", "Magic Number")
        yield UInt16(self, "nFib", "File Information Block (FIB) Version")
        yield UInt16(self, "nProduct", "Product Version")
        yield Enum(UInt16(self, "lid", "Language ID"), LANGUAGE_ID)
        yield Int16(self, "pnNext")

        yield Bit(self, "fDot", "Is the document a document template?")
        yield Bit(self, "fGlsy", "Is the document a glossary?")
        yield Bit(self, "fComplex", "Is the document in Complex format?")
        yield Bit(self, "fHasPic", "Does the document have embedded images?")
        yield Bits(self, "cQuickSaves", 4, "Number of times the document was quick-saved")
        yield Bit(self, "fEncrypted", "Is the document encrypted?")
        yield Bits(self, "reserved[]", 7)

        yield UInt16(self, "nFibBack")
        yield UInt32(self, "reserved[]")
        yield NullBytes(self, "rgwSpare", 6)

        yield UInt32(self, "fcMin", "File offset of first text character")
        yield UInt32(self, "fcMax", "File offset of last text character + 1")
        yield Int32(self, "cbMax", "File offset of last byte + 1")
        yield NullBytes(self, "fcSpare", 16)

        yield UInt32(self, "ccpText", "Length of main document text stream")
        yield Int32(self, "ccpFtn", "Length of footnote subdocument text stream")
        yield Int32(self, "ccpHdr", "Length of header subdocument text stream")
        yield Int32(self, "ccpMcr", "Length of macro subdocument text stream")
        yield Int32(self, "ccpAtn", "Length of annotation subdocument text stream")
        yield NullBytes(self, "ccpSpare", 16)

        yield FC_CB(self, "StshfOrig", "Original STSH allocation")
        yield FC_CB(self, "Stshf", "Current STSH allocation")
        yield FC_CB(self, "PlcffndRef", "Footnote reference PLC")
        yield FC_CB(self, "PlcffndTxt", "Footnote text PLC")
        yield FC_CB(self, "PlcfandRef", "Annotation reference PLC")
        yield FC_CB(self, "PlcfandTxt", "Annotation text PLC")
        yield FC_CB(self, "Plcfsed", "Section descriptor PLC")
        yield FC_CB(self, "Plcfpgd", "Page descriptor PLC")
        yield FC_CB(self, "Plcfphe", "Paragraph heights PLC")
        yield FC_CB(self, "Sttbfglsy", "Glossary string table")
        yield FC_CB(self, "Plcfglsy", "Glossary PLC")
        yield FC_CB(self, "Plcfhdd", "Header PLC")
        yield FC_CB(self, "PlcfbteChpx", "Character property bin table PLC")
        yield FC_CB(self, "PlcfbtePapx", "Paragraph property bin table PLC")
        yield FC_CB(self, "Plcfsea", "Private Use PLC")
        yield FC_CB(self, "Sttbfffn")
        yield FC_CB(self, "PlcffldMom")
        yield FC_CB(self, "PlcffldHdr")
        yield FC_CB(self, "PlcffldFtn")
        yield FC_CB(self, "PlcffldAtn")
        yield FC_CB(self, "PlcffldMcr")
        yield FC_CB(self, "Sttbfbkmk")
        yield FC_CB(self, "Plcfbkf")
        yield FC_CB(self, "Plcfbkl")
        yield FC_CB(self, "Cmds")
        yield FC_CB(self, "Plcmcr")
        yield FC_CB(self, "Sttbfmcr")
        yield FC_CB(self, "PrDrvr", "Printer Driver information")
        yield FC_CB(self, "PrEnvPort", "Printer environment for Portrait mode")
        yield FC_CB(self, "PrEnvLand", "Printer environment for Landscape mode")
        yield FC_CB(self, "Wss", "Window Save State")
        yield FC_CB(self, "Dop", "Document Property data")
        yield FC_CB(self, "SttbfAssoc")
        yield FC_CB(self, "Clx", "'Complex' file format data")
        yield FC_CB(self, "PlcfpgdFtn", "Footnote page descriptor PLC")
        yield FC_CB(self, "AutosaveSource", "Original filename for Autosave purposes")
        yield FC_CB(self, "Spare5")
        yield FC_CB(self, "Spare6")

        yield Int16(self, "wSpare4")
        yield UInt16(self, "pnChpFirst")
        yield UInt16(self, "pnPapFirst")
        yield UInt16(self, "cpnBteChp", "Count of CHPX FKPs recorded in file")
        yield UInt16(self, "cpnBtePap", "Count of PAPX FKPs recorded in file")

class SEPX(FieldSet):
    def createFields(self):
        yield UInt8(self, "size")
        self._size=(self['size'].value+1)*8
        yield RawBytes(self, "raw[]", self['size'].value)

class SEPXGroup(FieldSet):
    def __init__(self, parent, name, size, description=None):
        FieldSet.__init__(self, parent, name, description=description)
        self._size=size*8
    def createFields(self):
        while self.current_size < self.size:
            next=self.stream.readBytes(self.absolute_address+self.current_size,1)
            if next=='\x00':
                padding = paddingSize((self.absolute_address + self.current_size)//8, 512)
                if padding:
                    yield NullBytes(self, "padding[]", padding)
                if self.current_size >= self.size: break
            yield SEPX(self, "sepx[]")

class Word2DocumentParser(OLE2FragmentParser):
    MAGIC='\xdb\xa5' # 42459
    PARSER_TAGS = {
        "id": "word_v2_document",
        "min_size": 8,
        "magic": ((MAGIC, 0),),
        "file_ext": ("doc",),
        "description": "Microsoft Office Word Version 2.0 document",
    }
    endian = LITTLE_ENDIAN

    def __init__(self, stream, **args):
        OLE2FragmentParser.__init__(self, stream, **args)

    def validate(self):
        if self.stream.readBytes(0,2) != self.MAGIC:
            return "Invalid magic."
        if self['FIB/nFib'].value not in (45,):
            return "Unknown FIB version."
        return True

    def createFields(self):
        yield FIB(self, "FIB", "File Information Block")
        
        padding = (self['FIB/fcMin'].value - self.current_size//8)
        if padding:
            yield NullBytes(self, "padding[]", padding)
        if self['FIB/ccpText'].value:
            yield Bytes(self, "text", self['FIB/ccpText'].value)
        if self['FIB/ccpFtn'].value:
            yield Bytes(self, "text_footnote", self['FIB/ccpFtn'].value)
        if self['FIB/ccpHdr'].value:
            yield Bytes(self, "text_header", self['FIB/ccpHdr'].value)
        if self['FIB/ccpMcr'].value:
            yield Bytes(self, "text_macro", self['FIB/ccpMcr'].value)
        if self['FIB/ccpAtn'].value:
            yield Bytes(self, "text_annotation", self['FIB/ccpAtn'].value)

        padding = (self['FIB/fcMax'].value - self.current_size//8)
        if padding:
            yield RawBytes(self, "padding[]", padding)
        
        sepx_size = (self['FIB/pnChpFirst'].value*512 - self.current_size//8)
        if sepx_size:
            yield SEPXGroup(self, "sepx", sepx_size)

