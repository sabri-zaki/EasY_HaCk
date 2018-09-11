"""
Documents:

* libwx source code: see fib.c source code
* "Microsoft Word 97 Binary File Format"
   http://bio.gsi.de/DOCS/AIX/wword8.html

   Microsoft Word 97 (aka Version 8) for Windows and Macintosh. From the Office
   book, found in the Microsoft Office Development section in the MSDN Online
   Library. HTMLified June 1998. Revised Aug 1 1998, added missing Definitions
   section. Revised Dec 21 1998, added missing Document Properties (section).
"""

from hachoir_core.field import (FieldSet, Enum,
    Bit, Bits,
    UInt8, Int16, UInt16, UInt32, Int32,
    NullBytes, Bytes, RawBytes, PascalString8, PascalString16, CString, String,
    TimestampMac32, TimestampWin64)
from hachoir_core.text_handler import displayHandler
from hachoir_core.endian import LITTLE_ENDIAN
from hachoir_parser import guessParser
from hachoir_parser.misc.ole2_util import OLE2FragmentParser
from hachoir_parser.common.win32_lang_id import LANGUAGE_ID

CREATOR_ID={0x6A62: "Microsoft Word"}
class ShortArray(FieldSet):
    def createFields(self):
        yield UInt16(self, "csw", "Count of fields in the array of shorts")
        self._size = self['csw'].value*16+16
        yield Enum(UInt16(self, "wMagicCreated", "File creator ID"), CREATOR_ID)
        yield Enum(UInt16(self, "wMagicRevised", "File last modifier ID"), CREATOR_ID)
        yield UInt16(self, "wMagicCreatePrivate")
        yield UInt16(self, "wMagicCreatedPrivate")
        yield UInt16(self, "pnFbpChpFirst_W6")
        yield UInt16(self, "pnChpFirst_W6")
        yield UInt16(self, "cpnBteChp_W6")
        yield UInt16(self, "pnFbpPapFirst_W6")
        yield UInt16(self, "pnPapFirst_W6")
        yield UInt16(self, "cpnBtePap_W6")
        yield UInt16(self, "pnFbpLvcFirst_W6")
        yield UInt16(self, "pnLvcFirst_W6")
        yield UInt16(self, "cpnBteLvc_W6")
        yield Enum(UInt16(self, "lidFE", "Language ID if a Far East version of Word was used"), LANGUAGE_ID)
        while self.current_size < self.size:
            yield Int16(self, "unknown[]")

def buildDateHandler(v):
    md,y=divmod(v,100)
    m,d=divmod(md,100)
    if y < 60: y=2000+y
    else: y=1900+y
    return "%04i-%02i-%02i"%(y,m,d)

class LongArray(FieldSet):
    def createFields(self):
        yield UInt16(self, "clw", "Count of fields in the array of longs")
        self._size = self['clw'].value*32+16
        yield Int32(self, "cbMax", "Stream offset of last byte + 1")
        yield displayHandler(UInt32(self, "lProductCreated", "Date when the creator program was built"),buildDateHandler)
        yield displayHandler(UInt32(self, "lProductRevised", "Date when the last modifier program was built"),buildDateHandler)

        yield UInt32(self, "ccpText", "Length of main document text stream")
        yield Int32(self, "ccpFtn", "Length of footnote subdocument text stream")
        yield Int32(self, "ccpHdr", "Length of header subdocument text stream")
        yield Int32(self, "ccpMcr", "Length of macro subdocument text stream")
        yield Int32(self, "ccpAtn", "Length of annotation subdocument text stream")
        yield Int32(self, "ccpEdn", "Length of endnote subdocument text stream")
        yield Int32(self, "ccpTxbx", "Length of textbox subdocument text stream")
        yield Int32(self, "ccpHdrTxbx", "Length of header textbox subdocument text stream")
        yield Int32(self, "pnFbpChpFirst", "Start of CHPX (Character Property) sector chain (sector = 512-byte 'page')")
        yield Int32(self, "pnChpFirst", "First CHPX sector")
        yield Int32(self, "cpnBteChp", "Number of CHPX sectors in the file")
        yield Int32(self, "pnFbpPapFirst", "Start of PAPX (Paragraph Property) sector chain")
        yield Int32(self, "pnPapFirst", "First PAPX sector")
        yield Int32(self, "cpnBtePap", "Number of PAPX sectors in the file")
        yield Int32(self, "pnFbpLvcFirst", "Start of LVC sector chain")
        yield Int32(self, "pnLvcFirst", "First LVC sector")
        yield Int32(self, "cpnBteLvc", "Number of LVC sectors in the file")
        yield Int32(self, "fcIslandFirst")
        yield Int32(self, "fcIslandLim")
        while self.current_size < self.size:
            yield Int32(self, "unknown[]")

class FCLCB(FieldSet):
    static_size=64
    def createFields(self):
        yield Int32(self, "fc", "Table Stream Offset")
        yield UInt32(self, "lcb", "Byte Count")
    def createValue(self):
        return (self['fc'].value,self['lcb'].value)

class FCLCBArray(FieldSet):
    def createFields(self):
        yield UInt16(self, "cfclcb", "Count of fields in the array of FC/LCB pairs")
        self._size = self['cfclcb'].value*64+16
        
        yield FCLCB(self, "StshfOrig", "Original STSH allocation")
        yield FCLCB(self, "Stshf", "Current STSH allocation")
        yield FCLCB(self, "PlcffndRef", "Footnote reference (FRD) PLC")
        yield FCLCB(self, "PlcffndTxt", "Footnote text PLC")
        yield FCLCB(self, "PlcfandRef", "Annotation reference (ATRD) PLC")
        yield FCLCB(self, "PlcfandTxt", "Annotation text PLC")
        yield FCLCB(self, "Plcfsed", "Section descriptor (SED) PLC")
        yield FCLCB(self, "Plcpad", "No longer used; used to be Plcfpgd (Page descriptor PLC)")
        yield FCLCB(self, "Plcfphe", "Paragraph heights (PHE) PLC (only for Complex files)")
        yield FCLCB(self, "Sttbfglsy", "Glossary string table")
        yield FCLCB(self, "Plcfglsy", "Glossary PLC")
        yield FCLCB(self, "Plcfhdd", "Header (HDD) PLC")
        yield FCLCB(self, "PlcfbteChpx", "Character property bin table PLC")
        yield FCLCB(self, "PlcfbtePapx", "Paragraph property bin table PLC")
        yield FCLCB(self, "Plcfsea", "Private Use PLC")
        yield FCLCB(self, "Sttbfffn", "Font information STTB")
        yield FCLCB(self, "PlcffldMom", "Main document field position (FLD) PLC")
        yield FCLCB(self, "PlcffldHdr", "Header subdocument field position (FLD) PLC")
        yield FCLCB(self, "PlcffldFtn", "Footnote subdocument field position (FLD) PLC")
        yield FCLCB(self, "PlcffldAtn", "Annotation subdocument field position (FLD) PLC")
        yield FCLCB(self, "PlcffldMcr", "No longer used")
        yield FCLCB(self, "Sttbfbkmk", "Bookmark names STTB")
        yield FCLCB(self, "Plcfbkf", "Bookmark begin position (BKF) PLC")
        yield FCLCB(self, "Plcfbkl", "Bookmark end position (BKL) PLC")
        yield FCLCB(self, "Cmds", "Macro commands")
        yield FCLCB(self, "Plcmcr", "No longer used")
        yield FCLCB(self, "Sttbfmcr", "No longer used")
        yield FCLCB(self, "PrDrvr", "Printer Driver information")
        yield FCLCB(self, "PrEnvPort", "Printer environment for Portrait mode")
        yield FCLCB(self, "PrEnvLand", "Printer environment for Landscape mode")
        yield FCLCB(self, "Wss", "Window Save State")
        yield FCLCB(self, "Dop", "Document Property data")
        yield FCLCB(self, "SttbfAssoc", "Associated strings STTB")
        yield FCLCB(self, "Clx", "Complex file information")
        yield FCLCB(self, "PlcfpgdFtn", "Not used")
        yield FCLCB(self, "AutosaveSource", "Original filename for Autosave purposes")
        yield FCLCB(self, "GrpXstAtnOwners", "String Group for Annotation Owner Names")
        yield FCLCB(self, "SttbfAtnbkmk", "Annotation subdocument bookmark names STTB")
        yield FCLCB(self, "PlcdoaMom", "No longer used")
        yield FCLCB(self, "PlcdoaHdr", "No longer used")
        yield FCLCB(self, "PlcspaMom", "Main document File Shape (FSPA) PLC")
        yield FCLCB(self, "PlcspaHdr", "Header subdocument FSPA PLC")
        yield FCLCB(self, "PlcfAtnbkf", "Annotation subdocument bookmark begin position (BKF) PLC")
        yield FCLCB(self, "PlcfAtnbkl", "Annotation subdocument bookmark end position (BKL) PLC")
        yield FCLCB(self, "Pms", "Print Merge State")
        yield FCLCB(self, "FormFldSttbs", "Form field values STTB")
        yield FCLCB(self, "PlcfendRef", "Endnote Reference (FRD) PLC")
        yield FCLCB(self, "PlcfendTxt", "Endnote Text PLC")
        yield FCLCB(self, "PlcffldEdn", "Endnote subdocument field position (FLD) PLC)")
        yield FCLCB(self, "PlcfpgdEdn", "not used")
        yield FCLCB(self, "DggInfo", "Office Art Object Table Data")
        yield FCLCB(self, "SttbfRMark", "Editor Author Abbreviations STTB")
        yield FCLCB(self, "SttbCaption", "Caption Title STTB")
        yield FCLCB(self, "SttbAutoCaption", "Auto Caption Title STTB")
        yield FCLCB(self, "Plcfwkb", "WKB PLC")
        yield FCLCB(self, "Plcfspl", "Spell Check State PLC")
        yield FCLCB(self, "PlcftxbxTxt", "Text Box Text PLC")
        yield FCLCB(self, "PlcffldTxbx", "Text Box Reference (FLD) PLC")
        yield FCLCB(self, "PlcfhdrtxbxTxt", "Header Text Box Text PLC")
        yield FCLCB(self, "PlcffldHdrTxbx", "Header Text Box Reference (FLD) PLC")
        yield FCLCB(self, "StwUser", "Macro User storage")
        yield FCLCB(self, "Sttbttmbd", "Embedded TrueType Font Data")
        yield FCLCB(self, "Unused")
        yield FCLCB(self, "PgdMother", "Main text page descriptors PLF")
        yield FCLCB(self, "BkdMother", "Main text break descriptors PLF")
        yield FCLCB(self, "PgdFtn", "Footnote text page descriptors PLF")
        yield FCLCB(self, "BkdFtn", "Footnote text break descriptors PLF")
        yield FCLCB(self, "PgdEdn", "Endnote text page descriptors PLF")
        yield FCLCB(self, "BkdEdn", "Endnote text break descriptors PLF")
        yield FCLCB(self, "SttbfIntlFld", "Field keywords STTB")
        yield FCLCB(self, "RouteSlip", "Mailer Routing Slip")
        yield FCLCB(self, "SttbSavedBy", "STTB of names of users who have saved the document")
        yield FCLCB(self, "SttbFnm", "STTB of filenames of documents referenced by this one")
        yield FCLCB(self, "PlcfLst", "List Format information PLC")
        yield FCLCB(self, "PlfLfo", "List Format Override information PLC")
        yield FCLCB(self, "PlcftxbxBkd", "Main document textbox break table (BKD) PLC")
        yield FCLCB(self, "PlcftxbxHdrBkd", "Header subdocument textbox break table (BKD) PLC")
        yield FCLCB(self, "DocUndo", "Undo/Versioning data")
        yield FCLCB(self, "Rgbuse", "Undo/Versioning data")
        yield FCLCB(self, "Usp", "Undo/Versioning data")
        yield FCLCB(self, "Uskf", "Undo/Versioning data")
        yield FCLCB(self, "PlcupcRgbuse", "Undo/Versioning data")
        yield FCLCB(self, "PlcupcUsp", "Undo/Versioning data")
        yield FCLCB(self, "SttbGlsyStyle", "Glossary entry style names STTB")
        yield FCLCB(self, "Plgosl", "Grammar options PL")
        yield FCLCB(self, "Plcocx", "OCX data PLC")
        yield FCLCB(self, "PlcfbteLvc", "Character property bin table PLC")
        if self['../fMac'].value:
            yield TimestampMac32(self, "ftModified", "Date last modified")
            yield Int32(self, "padding[]")
        else:
            yield TimestampWin64(self, "ftModified", "Date last modified")
        yield FCLCB(self, "Plcflvc", "LVC PLC")
        yield FCLCB(self, "Plcasumy", "Autosummary PLC")
        yield FCLCB(self, "Plcfgram", "Grammar check PLC")
        yield FCLCB(self, "SttbListNames", "List names STTB")
        yield FCLCB(self, "SttbfUssr", "Undo/Versioning data")
        while self.current_size < self.size:
            yield FCLCB(self, "unknown[]")

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
        yield Bits(self, "fWhichTblStm", 1, "Which table stream (0Table or 1Table) to use")
        yield Bit(self, "fReadOnlyRecommended", "Should the file be opened read-only?")
        yield Bit(self, "fWriteReservation", "Is the file write-reserved?")
        yield Bit(self, "fExtChar", "Does the file use an extended character set?")
        yield Bit(self, "fLoadOverride")
        yield Bit(self, "fFarEast")
        yield Bit(self, "fCrypto")

        yield UInt16(self, "nFibBack", "Document is backwards compatible down to this FIB version")
        yield UInt32(self, "lKey", "File encryption key (only if fEncrypted)")
        yield Enum(UInt8(self, "envr", "Document creation environment"), {0:'Word for Windows',1:'Macintosh Word'})

        yield Bit(self, "fMac", "Was this file last saved on a Mac?")
        yield Bit(self, "fEmptySpecial")
        yield Bit(self, "fLoadOverridePage")
        yield Bit(self, "fFutureSavedUndo")
        yield Bit(self, "fWord97Save")
        yield Bits(self, "fSpare0", 3)
        CHARSET={0:'Windows ANSI',256:'Macintosh'}
        yield Enum(UInt16(self, "chse", "Character set for document text"),CHARSET)
        yield Enum(UInt16(self, "chsTables", "Character set for internal table text"),CHARSET)
        yield UInt32(self, "fcMin", "File offset for the first character of text")
        yield UInt32(self, "fcMax", "File offset for the last character of text + 1")

        yield ShortArray(self, "array1", "Array of shorts")
        yield LongArray(self, "array2", "Array of longs")
        yield FCLCBArray(self, "array3", "Array of File Offset/Byte Count (FC/LCB) pairs")

def getRootParser(ole2):
    return guessParser(ole2["root[0]"].getSubIStream())

def getOLE2Parser(ole2, path):
    name = path+"[0]"
    if name in ole2:
        fragment = ole2[name]
    else:
        fragment = getRootParser(ole2)[name]
    return guessParser(fragment.getSubIStream())

class WordDocumentParser(OLE2FragmentParser):
    MAGIC='\xec\xa5' # 42476
    PARSER_TAGS = {
        "id": "word_document",
        "min_size": 8,
        "magic": ((MAGIC, 0),),
        "description": "Microsoft Office Word document",
    }
    endian = LITTLE_ENDIAN

    def __init__(self, stream, **args):
        OLE2FragmentParser.__init__(self, stream, **args)

    def validate(self):
        if self.stream.readBytes(0,2) != self.MAGIC:
            return "Invalid magic."
        if self['FIB/nFib'].value not in (192,193):
            return "Unknown FIB version."
        return True

    def createFields(self):
        yield FIB(self, "FIB", "File Information Block")
        table = getOLE2Parser(self.ole2, "table"+str(self["FIB/fWhichTblStm"].value))

        padding = (self['FIB/fcMin'].value - self.current_size//8)
        if padding:
            yield NullBytes(self, "padding[]", padding)
        
        # Guess whether the file uses UTF16 encoding.
        is_unicode = False
        if self['FIB/array2/ccpText'].value*2 == self['FIB/fcMax'].value - self['FIB/fcMin'].value:
            is_unicode = True
        for fieldname, textname in [('Text','text'),('Ftn','text_footnote'),
        ('Hdr','text_header'),('Mcr','text_macro'),('Atn','text_annotation'),
        ('Edn','text_endnote'),('Txbx','text_textbox'),('HdrTxbx','text_header_textbox')]:
            size = self['FIB/array2/ccp'+fieldname].value
            if size:
                if is_unicode:
                    yield String(self, textname, size*2, charset="UTF-16-LE")
                else:
                    yield Bytes(self, textname, size)

        padding = (self['FIB/fcMax'].value - self.current_size//8)
        if padding:
            yield RawBytes(self, "padding[]", padding)

class WidePascalString16(String):
    def __init__(self, parent, name, description=None,
    strip=None, nbytes=None, truncate=None):
        Bytes.__init__(self, parent, name, 1, description)
        
        self._format = "WidePascalString16"
        self._strip = strip
        self._truncate = truncate
        self._character_size = 2
        self._charset = "UTF-16-LE"
        self._content_offset = 2
        self._content_size = self._character_size * self._parent.stream.readBits(
            self.absolute_address, self._content_offset*8, self._parent.endian)
        self._size = (self._content_size + self.content_offset) * 8

class TableParsers(object):
    class Bte(FieldSet):
        'Bin Table Entry'
        static_size = 32
        def createFields(self):
            yield Bits(self, "pn", 22, "Referenced page number")
            yield Bits(self, "unused", 10)

        def createValue(self):
            return self["pn"].value

    class Ffn(FieldSet):
        'Font Family Name'
        def createFields(self):
            yield UInt8(self, "size", "Total length of this FFN in bytes, minus 1")
            self._size = self["size"].value * 8 + 8
            yield Bits(self, "prq", 2, "Pitch request")
            yield Bit(self, "fTrueType", "Is font a TrueType font?")
            yield Bits(self, "reserved[]", 1)
            yield Bits(self, "ff", 3, "Font Family ID")
            yield Bits(self, "reserved[]", 1)
            yield UInt16(self, "wWeight", "Base weight of font")
            yield UInt8(self, "chs", "Character set identifier")
            yield UInt8(self, "ixchSzAlt", "Index into name to the name of the alternate font")
            yield RawBytes(self, "panose", 10)
            yield RawBytes(self, "fs", 24, "Font Signature")
            yield CString(self, "name", charset="UTF-16-LE")
            if self["ixchSzAlt"].value != 0:
                yield CString(self, "nameAlt", charset="UTF-16-LE")

        def createValue(self):
            return self["name"].value

    class Sttbf(FieldSet):
        'String Table stored in File'
        SttbfAssocDESC = {
            0: "FileNext: unused",
            1: "Dot: filename of associated template",
            2: "Title: title of document",
            3: "Subject: subject of document",
            4: "KeyWords: keywords of document",
            5: "Comments: comments of document",
            6: "Author: author of document",
            7: "LastRevBy: name of person who last revised the document",
            8: "DataDoc: filename of data document",
            9: "HeaderDoc: filename of header document",
            10: "Criteria1: packed string used by print merge record selection",
            11: "Criteria2: packed string used by print merge record selection",
            12: "Criteria3: packed string used by print merge record selection",
            13: "Criteria4: packed string used by print merge record selection",
            14: "Criteria5: packed string used by print merge record selection",
            15: "Criteria6: packed string used by print merge record selection",
            16: "Criteria7: packed string used by print merge record selection",
            17: "Max: maximum number of strings in string table",
        }

        def createFields(self):
            if self.stream.readBytes(self.absolute_address, 2) == "\xff\xff":
                yield Int16(self, "utf16_marker", "If this field is present, the Sttbf contains UTF-16 data.")
                self.is_utf16 = True
            else:
                self.is_utf16 = False
            yield UInt16(self, "count", "Number of strings in this Sttbf")
            extra_data_field = UInt16(self, "extra_data_len", "Size of optional extra data after each string")
            yield extra_data_field
            extra_data_len = extra_data_field.value
            for i in xrange(self["count"].value):
                if self.name == "SttbfAssoc":
                    desc = self.SttbfAssocDESC.get(i, None)
                else:
                    desc = None
                if self.name == "Sttbfffn":
                    yield TableParsers.Ffn(self, "string[]", desc)
                elif self.is_utf16:
                    yield WidePascalString16(self, "string[]", desc)
                else:
                    yield PascalString8(self, "string[]", desc)
                if extra_data_len:
                    yield RawBytes(self, "extra[]", extra_data_len)

    class Plcf(FieldSet):
        'Plex of CPs/FCs stored in file'
        def createFields(self):
            if self.size is None:
                return
            chunk_parser = None
            size = None
            if self.name.startswith("Plcfbte"):
                chunk_parser = TableParsers.Bte
            if not chunk_parser:
                return
            if size is None:
                size = chunk_parser.static_size // 8
            n = (self.size / 8 - 4) / (4 + size)
            for i in xrange(n+1):
                yield UInt32(self, "cp_fc[]", "CP or FC value")
            for i in xrange(n):
                yield chunk_parser(self, "obj[]")

class WordTableParser(OLE2FragmentParser):
    def createFields(self):
        word_doc = getOLE2Parser(self.ole2, "word_doc")
        if word_doc["FIB/fWhichTblStm"].value != int(self.ole2name[0]):
            yield RawBytes(self, "inactive_table", self.datasize)
            return
        for fclcb in word_doc["FIB/array3"]:
            if not isinstance(fclcb, FCLCB):
                continue
            if fclcb["fc"].value < 0 or fclcb["lcb"].value <= 0:
                continue
            self.seekByte(fclcb["fc"].value, relative=False)
            if fclcb.name.startswith("Sttb"):
                yield TableParsers.Sttbf(self, fclcb.name, size=fclcb["lcb"].value * 8)
            elif fclcb.name.startswith("Plc"):
                yield TableParsers.Plcf(self, fclcb.name, size=fclcb["lcb"].value * 8)
            else:
                yield RawBytes(self, fclcb.name, fclcb["lcb"].value, fclcb.description)
