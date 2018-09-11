"""
Parsers for the different streams and fragments found in an OLE2 file.

Documents:
 - goffice source code
 - Microsoft Office PowerPoint 97-2007 Binary File Format (.ppt) Specification
    http://download.microsoft.com/download/0/B/E/0BE8BDD7-E5E8-422A-ABFD-4342ED7AD886/PowerPoint97-2007BinaryFileFormat(ppt)Specification.pdf

Author: Robert Xiao, Victor Stinner
Creation: 8 january 2005
"""

from hachoir_core.field import (SubFile, FieldSet,
    UInt8, UInt16, Int32, UInt32, Enum, String, CString,
    Bits, RawBytes)
from hachoir_core.text_handler import textHandler, hexadecimal
from hachoir_parser.misc.ole2_util import OLE2FragmentParser, RawParser
from hachoir_core.stream import StringInputStream
from hachoir_parser.misc.msoffice_summary import Summary, CompObj
from hachoir_parser.misc.word_doc import WordDocumentParser, WordTableParser

class RootEntry(OLE2FragmentParser):
    ENDIAN_CHECK=False

    def createFields(self):
        for index, property in enumerate(self.ole2.properties):
            if index == 0:
                continue
            try:
                name,parser = PROPERTY_NAME[property["name"].value]
            except LookupError:
                name = property.name+"content"
                parser = RawParser
            for field in self.parseProperty(property, name, parser):
                yield field
    def seekSBlock(self, block):
        self.seekBit(block * self.ole2.ss_size)

    def parseProperty(self, property, name_prefix, parser=RawParser):
        ole2 = self.ole2
        if not property["size"].value:
            return
        if property["size"].value >= ole2["header/threshold"].value:
            return
        name = "%s[]" % name_prefix
        first = None
        previous = None
        size = 0
        fragment_group = None
        chain = ole2.getChain(property["start"].value, ole2.ss_fat)
        while True:
            try:
                block = chain.next()
                contiguous = False
                if first is None:
                    first = block
                    contiguous = True
                if previous is not None and block == (previous+1):
                    contiguous = True
                if contiguous:
                    previous = block
                    size += ole2.ss_size
                    continue
            except StopIteration:
                block = None
            if first is None:
                break
            self.seekSBlock(first)
            desc = "Small blocks %s..%s (%s)" % (first, previous, previous-first+1)
            desc += " of %s bytes" % (ole2.ss_size//8)
            field = CustomFragment(self, name, size, parser, desc, fragment_group)
            yield field
            if not fragment_group:
                fragment_group = field.group
                fragment_group.args["datasize"] = property["size"].value
                fragment_group.args["ole2name"] = property["name"].value
            if block is None:
                break
            first = block
            previous = block
            size = ole2.ss_size

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
        self.args["ole2"] = self.items[0].root
        tags = {"class": self.parser, "args": self.args}
        tags = tags.iteritems()
        return StringInputStream(data, "<fragment group>", tags=tags)

class CustomFragment(FieldSet):
    def __init__(self, parent, name, size, parser, description=None, group=None):
        FieldSet.__init__(self, parent, name, description, size=size)
        if not group:
            group = FragmentGroup(parser)
        self.group = group
        self.group.add(self)

    def createFields(self):
        yield RawBytes(self, "rawdata", self.size//8)

    def _createInputStream(self, **args):
        return self.group.createInputStream()

class Pictures(OLE2FragmentParser):
    class Picture(FieldSet):
        def createFields(self):
            yield RawBytes(self, "identifier", 4, "some kind of marker (A0461DF0)")
            yield UInt32(self, "size")
            yield RawBytes(self, "unknown[]", 16)
            yield RawBytes(self, "unknown[]", 1)
            yield SubFile(self, "image", self["size"].value-17, "Image Data")
    ENDIAN_CHECK=False

    def createFields(self):
        pos=0
        while pos//8 < self.datasize:
            newpic=Pictures.Picture(self, "picture[]")
            yield newpic
            pos+=newpic.size

class PowerPointDocument(OLE2FragmentParser):
    OBJ_TYPES={ 0:"Unknown",
                1000:"Document",
                1001:"DocumentAtom",
                1002:"EndDocument",
                1003:"SlidePersist",
                1004:"SlideBase",
                1005:"SlideBaseAtom",
                1006:"Slide",
                1007:"SlideAtom",
                1008:"Notes",
                1009:"NotesAtom",
                1010:"Environment",
                1011:"SlidePersistAtom",
                1012:"Scheme",
                1013:"SchemeAtom",
                1014:"DocViewInfo",
                1015:"SSlideLayoutAtom",
                1016:"MainMaster",
                1017:"SSSlideInfoAtom",
                1018:"SlideViewInfo",
                1019:"GuideAtom",
                1020:"ViewInfo",
                1021:"ViewInfoAtom",
                1022:"SlideViewInfoAtom",
                1023:"VBAInfo",
                1024:"VBAInfoAtom",
                1025:"SSDocInfoAtom",
                1026:"Summary",
                1027:"Texture",
                1028:"VBASlideInfo",
                1029:"VBASlideInfoAtom",
                1030:"DocRoutingSlip",
                1031:"OutlineViewInfo",
                1032:"SorterViewInfo",
                1033:"ExObjList",
                1034:"ExObjListAtom",
                1035:"PPDrawingGroup", #FIXME: Office Art File Format Docu
                1036:"PPDrawing", #FIXME: Office Art File Format Docu
                1038:"Theme",
                1039:"ColorMapping",
                1040:"NamedShows", # don't know if container
                1041:"NamedShow",
                1042:"NamedShowSlides", # don't know if container
                1052:"OriginalMainMasterId",
                1053:"CompositeMasterId",
                1054:"RoundTripContentMasterInfo12",
                1055:"RoundTripShapeId12",
                1056:"RoundTripHFPlaceholder12",
                1058:"RoundTripContentMasterId12",
                1059:"RoundTripOArtTextStyles12",
                1060:"HeaderFooterDefaults12",
                1061:"DocFlags12",
                1062:"RoundTripShapeCheckSumForCustomLayouts12",
                1063:"RoundTripNotesMasterTextStyles12",
                1064:"RoundTripCustomTableStyles12",
                2000:"List",
                2005:"FontCollection",
                2017:"ListPlaceholder",
                2019:"BookmarkCollection",
                2020:"SoundCollection",
                2021:"SoundCollAtom",
                2022:"Sound",
                2023:"SoundData",
                2025:"BookmarkSeedAtom",
                2026:"GuideList",
                2028:"RunArray",
                2029:"RunArrayAtom",
                2030:"ArrayElementAtom",
                2031:"Int4ArrayAtom",
                2032:"ColorSchemeAtom",
                3008:"OEShape",
                3009:"ExObjRefAtom",
                3011:"OEPlaceholderAtom",
                3020:"GrColor",
                3024:"GPointAtom",
                3025:"GrectAtom",
                3031:"GRatioAtom",
                3032:"Gscaling",
                3034:"GpointAtom",
                3035:"OEShapeAtom",
                3037:"OEPlaceholderNewPlaceholderId12",
                3998:"OutlineTextRefAtom",
                3999:"TextHeaderAtom",
                4000:"TextCharsAtom",
                4001:"StyleTextPropAtom",
                4002:"BaseTextPropAtom",
                4003:"TxMasterStyleAtom",
                4004:"TxCFStyleAtom",
                4005:"TxPFStyleAtom",
                4006:"TextRulerAtom",
                4007:"TextBookmarkAtom",
                4008:"TextBytesAtom",
                4009:"TxSIStyleAtom",
                4010:"TextSpecInfoAtom",
                4011:"DefaultRulerAtom",
                4023:"FontEntityAtom",
                4024:"FontEmbeddedData",
                4025:"TypeFace",
                4026:"CString",
                4027:"ExternalObject",
                4033:"MetaFile",
                4034:"ExOleObj",
                4035:"ExOleObjAtom",
                4036:"ExPlainLinkAtom",
                4037:"CorePict",
                4038:"CorePictAtom",
                4039:"ExPlainAtom",
                4040:"SrKinsoku",
                4041:"HandOut",
                4044:"ExEmbed",
                4045:"ExEmbedAtom",
                4046:"ExLink",
                4047:"ExLinkAtom_old",
                4048:"BookmarkEntityAtom",
                4049:"ExLinkAtom",
                4050:"SrKinsokuAtom",
                4051:"ExHyperlinkAtom",
                4053:"ExPlain",
                4054:"ExPlainLink",
                4055:"ExHyperlink",
                4056:"SlideNumberMCAtom",
                4057:"HeadersFooters",
                4058:"HeadersFootersAtom",
                4062:"RecolorEntryAtom",
                4063:"TxInteractiveInfoAtom",
                4065:"EmFormatAtom",
                4066:"CharFormatAtom",
                4067:"ParaFormatAtom",
                4068:"MasterText",
                4071:"RecolorInfoAtom",
                4073:"ExQuickTime",
                4074:"ExQuickTimeMovie",
                4075:"ExQuickTimeMovieData",
                4076:"ExSubscription",
                4077:"ExSubscriptionSection",
                4078:"ExControl",
                4080:"SlideListWithText",
                4081:"AnimationInfoAtom",
                4082:"InteractiveInfo",
                4083:"InteractiveInfoAtom",
                4084:"SlideList",
                4085:"UserEditAtom",
                4086:"CurrentUserAtom",
                4087:"DateTimeMCAtom",
                4088:"GenericDateMCAtom",
                4090:"FooterMCAtom",
                4091:"ExControlAtom",
                4100:"ExMediaAtom",
                4101:"ExVideo",
                4102:"ExAviMovie",
                4103:"ExMCIMovie",
                4109:"ExMIDIAudio",
                4110:"ExCDAudio",
                4111:"ExWAVAudioEmbedded",
                4112:"ExWAVAudioLink",
                4113:"ExOleObjStg",
                4114:"ExCDAudioAtom",
                4115:"ExWAVAudioEmbeddedAtom",
                4116:"AnimationInfoAtom",
                4117:"RTFDateTimeMCAtom",
                5000:"ProgTags", # don't know if container
                5001:"ProgStringTag",
                5002:"ProgBinaryTag",
                5003:"BinaryTagData",
                6000:"PrintOptions",
                6001:"PersistPtrFullBlock", # don't know if container
                6002:"PersistPtrIncrementalBlock", # don't know if container
                10000:"RulerIndentAtom",
                10001:"GScalingAtom",
                10002:"GRColorAtom",
                10003:"GLPointAtom",
                10004:"GlineAtom",
                11019:"AnimationAtom12",
                11021:"AnimationHashAtom12",
                14100:"SlideSyncInfo12",
                14101:"SlideSyncInfoAtom12",
                0xf000:"EscherDggContainer", # Drawing Group Container 
                0xf006:"EscherDgg",
                0xf016:"EscherCLSID",
                0xf00b:"EscherOPT",
                0xf001:"EscherBStoreContainer",
                0xf007:"EscherBSE",
                0xf018:"EscherBlip_START", # Blip types are between 
                0xf117:"EscherBlip_END", # these two values 
                0xf002:"EscherDgContainer", # Drawing Container 
                0xf008:"EscherDg",
                0xf118:"EscherRegroupItems",
                0xf120:"EscherColorScheme", # bug in docs 
                0xf003:"EscherSpgrContainer",
                0xf004:"EscherSpContainer",
                0xf009:"EscherSpgr",
                0xf00a:"EscherSp",
                0xf00c:"EscherTextbox",
                0xf00d:"EscherClientTextbox",
                0xf00e:"EscherAnchor",
                0xf00f:"EscherChildAnchor",
                0xf010:"EscherClientAnchor",
                0xf011:"EscherClientData",
                0xf005:"EscherSolverContainer",
                0xf012:"EscherConnectorRule", # bug in docs 
                0xf013:"EscherAlignRule",
                0xf014:"EscherArcRule",
                0xf015:"EscherClientRule",
                0xf017:"EscherCalloutRule",
                0xf119:"EscherSelection",
                0xf11a:"EscherColorMRU",
                0xf11d:"EscherDeletedPspl", # bug in docs 
                0xf11e:"EscherSplitMenuColors",
                0xf11f:"EscherOleObject",
                0xf122:"EscherUserDefined"}
    class CurrentUserAtom(FieldSet):
        def createFields(self):
            yield UInt32(self, "size")
            yield textHandler(UInt32(self, "magic", "0xe391c05f for normal PPT, 0xf3d1c4df for encrypted PPT"), hexadecimal)
            yield UInt32(self, "offsetToCurrentEdit", "Offset in main stream to current edit field")
            yield UInt16(self, "lenUserName", "Length of user name")
            yield UInt16(self, "docFileVersion", "1012 for PP97+")
            yield UInt8(self, "majorVersion", "3 for PP97+")
            yield UInt8(self, "minorVersion", "0 for PP97+")
            yield UInt16(self, "unknown")
            yield String(self, "userName", self["lenUserName"].value, "ANSI version of the username")
            yield UInt32(self, "relVersion", "Release version: 8 for regular PPT file, 9 for multiple-master PPT file")

    class PowerPointObject(FieldSet):
        def createFields(self):
            yield Bits(self, "version", 4)
            yield Bits(self, "instance", 12)
            yield Enum(UInt16(self, "type"),PowerPointDocument.OBJ_TYPES)
            yield UInt32(self, "length")
            self._size = self["length"].value * 8 + 64
            obj_type = self["type"].display
            obj_len = self["length"].value
            # type 1064 (RoundTripCustomTableStyles12) may appear to be a container, but it is not.
            if self["version"].value==0xF and self["type"].value != 1064:
                while (self.current_size)//8 < obj_len+8:
                    yield PowerPointDocument.PowerPointObject(self, "object[]")
            elif obj_len:
                if obj_type=="FontEntityAtom":
                    yield String(self, "data", obj_len, charset="UTF-16-LE", truncate="\0", strip="\0")
                elif obj_type=="TextCharsAtom":
                    yield String(self, "data", obj_len, charset="UTF-16-LE")
                elif obj_type=="TextBytesAtom":
                    yield String(self, "data", obj_len, charset="ASCII")
                elif hasattr(PowerPointDocument, obj_type):
                    field = getattr(PowerPointDocument, obj_type)(self, "data")
                    field._size = obj_len * 8
                    yield field
                else:
                    yield RawBytes(self, "data", obj_len)
        def createDescription(self):
            if self["version"].value==0xF:
                return "PowerPoint Object Container; instance %s, type %s"%(self["instance"].value,self["type"].display)
            return "PowerPoint Object; version %s, instance %s, type %s"%(self["version"].value,self["instance"].value,self["type"].display)
    ENDIAN_CHECK=False
    OS_CHECK=False
    def createFields(self):
        pos=0
        while pos//8 < self.datasize:
            newobj=PowerPointDocument.PowerPointObject(self, "object[]")
            yield newobj
            pos+=newobj.size

class CurrentUser(OLE2FragmentParser):
    def createFields(self):
        yield PowerPointDocument.PowerPointObject(self, "current_user")
        if self.current_size < self.size:
            yield String(self, "unicode_name", self["current_user/data/lenUserName"].value * 2, charset="UTF-16-LE")
        

class ExcelWorkbook(OLE2FragmentParser):
    BIFF_TYPES={0x000:"DIMENSIONS_v0",
                0x200:"DIMENSIONS_v2",
                0x001:"BLANK_v0",
                0x201:"BLANK_v2",
                0x002:"INTEGER",
                0x003:"NUMBER_v0",
                0x203:"NUMBER_v2",
                0x004:"LABEL_v0",
                0x204:"LABEL_v2",
                0x005:"BOOLERR_v0",
                0x205:"BOOLERR_v2",
                0x006:"FORMULA_v0",
                0x206:"FORMULA_v2",
                0x406:"FORMULA_v4",
                0x007:"STRING_v0",
                0x207:"STRING_v2",
                0x008:"ROW_v0",
                0x208:"ROW_v2",
                0x009:"BOF_v0",
                0x209:"BOF_v2",
                0x409:"BOF_v4",
                0x809:"BOF_v8",
                0x00a:"EOF",
                0x00b:"INDEX_v0",
                0x20b:"INDEX_v2",
                0x00c:"CALCCOUNT",
                0x00d:"CALCMODE",
                0x00e:"PRECISION",
                0x00f:"REFMODE",
                0x010:"DELTA",
                0x011:"ITERATION",
                0x012:"PROTECT",
                0x013:"PASSWORD",
                0x014:"HEADER",
                0x015:"FOOTER",
                0x016:"EXTERNCOUNT",
                0x017:"EXTERNSHEET",
                0x018:"NAME_v0",
                0x218:"NAME_v2",
                0x019:"WINDOWPROTECT",
                0x01a:"VERTICALPAGEBREAKS",
                0x01b:"HORIZONTALPAGEBREAKS",
                0x01c:"NOTE",
                0x01d:"SELECTION",
                0x01e:"FORMAT_v0",
                0x41e:"FORMAT_v4",
                0x01f:"FORMATCOUNT",	# Undocumented 
                0x020:"COLUMNDEFAULT",	# Undocumented 
                0x021:"ARRAY_v0",
                0x221:"ARRAY_v2",
                0x022:"1904",
                0x023:"EXTERNNAME_v0",
                0x223:"EXTERNNAME_v2",
                0x024:"COLWIDTH",	# Undocumented 
                0x025:"DEFAULTROWHEIGHT_v0",
                0x225:"DEFAULTROWHEIGHT_v2",
                0x026:"LEFT_MARGIN",
                0x027:"RIGHT_MARGIN",
                0x028:"TOP_MARGIN",
                0x029:"BOTTOM_MARGIN",
                0x02a:"PRINTHEADERS",
                0x02b:"PRINTGRIDLINES",
                0x02f:"FILEPASS",
                0x031:"FONT_v0",
                0x231:"FONT_v2",
                0x032:"FONTCOUNT",	# Undocumented 
                0x033:"PRINTSIZE",	# Undocumented 
                0x036:"TABLE_v0",
                0x236:"TABLE_v2",
                0x037:"TABLE2",	# OOo has docs 
                0x038:"WNDESK",	# Undocumented 
                0x039:"ZOOM",	# Undocumented 
                0x03a:"BEGINPREF",	# Undocumented 
                0x03b:"ENDPREF",	# Undocumented 
                0x03c:"CONTINUE",
                0x03d:"WINDOW1",
                0x03e:"WINDOW2_v0",
                0x23e:"WINDOW2_v2",
                0x03f:"PANE_V2",	# Undocumented 
                0x040:"BACKUP",
                0x041:"PANE",
                0x042:"CODEPAGE",
                0x043:"XF_OLD_v0",
                0x243:"XF_OLD_v2",
                0x443:"XF_OLD_v4",
                0x044:"XF_INDEX",
                0x045:"FONT_COLOR",
                0x04d:"PLS",
                0x050:"DCON",
                0x051:"DCONREF",
                0x052:"DCONNAME",
                0x055:"DEFCOLWIDTH",
                0x059:"XCT",
                0x05a:"CRN",
                0x05b:"FILESHARING",
                0x05c:"WRITEACCESS",
                0x05d:"OBJ",
                0x05e:"UNCALCED",
                0x05f:"SAVERECALC",
                0x060:"TEMPLATE",
                0x061:"INTL",	# Undocumented 
                0x862:"TAB_COLOR",	# Undocumented, OO calls it SHEETLAYOUT 
                0x063:"OBJPROTECT",
                0x07d:"COLINFO",
                0x27e:"RK", # Odd that there is no 0x7e 
                0x07f:"IMDATA",
                0x080:"GUTS",
                0x081:"WSBOOL",
                0x082:"GRIDSET",
                0x083:"HCENTER",
                0x084:"VCENTER",
                0x085:"BOUNDSHEET",
                0x086:"WRITEPROT",
                0x087:"ADDIN",
                0x088:"EDG",
                0x089:"PUB",
                0x08c:"COUNTRY",
                0x08d:"HIDEOBJ",
                0x08e:"BUNDLESOFFSET",	# Undocumented 
                0x08f:"BUNDLEHEADER",	# Undocumented 
                0x090:"SORT",
                0x091:"SUB",
                0x092:"PALETTE",
                0x293:"STYLE", # Odd that there is no 0x93 
                0x094:"LHRECORD",
                0x095:"LHNGRAPH",
                0x096:"SOUND",
                0x097:"SYNC",	# Undocumented 
                0x098:"LPR",
                0x099:"STANDARDWIDTH",
                0x09a:"FNGROUPNAME",
                0x09b:"FILTERMODE",
                0x09c:"FNGROUPCOUNT",
                0x09d:"AUTOFILTERINFO",
                0x09e:"AUTOFILTER",
                0x0a0:"SCL",
                0x0a1:"SETUP",
                0x0a4:"TOOLBARVER",	# Undocumented 
                0x0a9:"COORDLIST",
                0x0ab:"GCW",
                0x0ae:"SCENMAN",
                0x0af:"SCENARIO",
                0x0b0:"SXVIEW",
                0x0b1:"SXVD",
                0x0b2:"SXVI",
                0x0b3:"SXSI",	# Undocumented 
                0x0b4:"SXIVD",
                0x0b5:"SXLI",
                0x0b6:"SXPI",
                0x0b7:"FACENUM",	# Undocumented
                0x0b8:"DOCROUTE",
                0x0b9:"RECIPNAME",
                0x0ba:"SSLIST",	# Undocumented 
                0x0bb:"MASKIMDATA",	# Undocumented 
                0x4bc:"SHRFMLA",
                0x0bd:"MULRK",
                0x0be:"MULBLANK",
                0x0bf:"TOOLBARHDR",	# Undocumented 
                0x0c0:"TOOLBAREND",	# Undocumented 
                0x0c1:"MMS",
                0x0c2:"ADDMENU",
                0x0c3:"DELMENU",
                0x0c4:"TIPHISTORY",	# Undocumented 
                0x0c5:"SXDI",
                0x0c6:"SXDB",
                0x0c7:"SXFDB",	# guessed 
                0x0c8:"SXDDB",	# guessed 
                0x0c9:"SXNUM",	# guessed 
                0x0ca:"SXBOOL",	# guessed 
                0x0cb:"SXERR",	# guessed 
                0x0cc:"SXINT",	# guessed 
                0x0cd:"SXSTRING",
                0x0ce:"SXDTR",	# guessed 
                0x0cf:"SXNIL",	# guessed 
                0x0d0:"SXTBL",
                0x0d1:"SXTBRGIITM",
                0x0d2:"SXTBPG",
                0x0d3:"OBPROJ",
                0x0d5:"SXIDSTM",
                0x0d6:"RSTRING",
                0x0d7:"DBCELL",
                0x0d8:"SXNUMGROUP",	# from OO : numerical grouping in pivot cache field 
                0x0da:"BOOKBOOL",
                0x0dc:"PARAMQRY",	# DUPLICATE dc 
                0x0dc:"SXEXT",	# DUPLICATE dc 
                0x0dd:"SCENPROTECT",
                0x0de:"OLESIZE",
                0x0df:"UDDESC",
                0x0e0:"XF",
                0x0e1:"INTERFACEHDR",
                0x0e2:"INTERFACEEND",
                0x0e3:"SXVS",
                0x0e5:"MERGECELLS",	# guessed 
                0x0e9:"BG_PIC",	# Undocumented 
                0x0ea:"TABIDCONF",
                0x0eb:"MS_O_DRAWING_GROUP",
                0x0ec:"MS_O_DRAWING",
                0x0ed:"MS_O_DRAWING_SELECTION",
                0x0ef:"PHONETIC",	# semi-Undocumented 
                0x0f0:"SXRULE",
                0x0f1:"SXEX",
                0x0f2:"SXFILT",
                0x0f6:"SXNAME",
                0x0f7:"SXSELECT",
                0x0f8:"SXPAIR",
                0x0f9:"SXFMLA",
                0x0fb:"SXFORMAT",
                0x0fc:"SST",
                0x0fd:"LABELSST",
                0x0ff:"EXTSST",
                0x100:"SXVDEX",
                0x103:"SXFORMULA",
                0x122:"SXDBEX",
                0x137:"CHTRINSERT",
                0x138:"CHTRINFO",
                0x13B:"CHTRCELLCONTENT",
                0x13d:"TABID",
                0x140:"CHTRMOVERANGE",
                0x14D:"CHTRINSERTTAB",
                0x15F:"LABELRANGES",
                0x160:"USESELFS",
                0x161:"DSF",
                0x162:"XL5MODIFY",
                0x196:"CHTRHEADER",
                0x1a5:"FILESHARING2",
                0x1a9:"USERDBVIEW",
                0x1aa:"USERSVIEWBEGIN",
                0x1ab:"USERSVIEWEND",
                0x1ad:"QSI",
                0x1ae:"SUPBOOK",
                0x1af:"PROT4REV",
                0x1b0:"CONDFMT",
                0x1b1:"CF",
                0x1b2:"DVAL",
                0x1b5:"DCONBIN",
                0x1b6:"TXO",
                0x1b7:"REFRESHALL",
                0x1b8:"HLINK",
                0x1ba:"CODENAME",	# TYPO in MS Docs 
                0x1bb:"SXFDBTYPE",
                0x1bc:"PROT4REVPASS",
                0x1be:"DV",
                0x1c0:"XL9FILE",
                0x1c1:"RECALCID",
                0x800:"LINK_TIP",	# follows an hlink 
                0x802:"UNKNOWN_802",	# OO exports it but has not name or docs 
                0x803:"WQSETT",	# OO named it and can export it, but does not include it in the docs 
                0x804:"WQTABLES",	# OO named it and can export it, but does not include it in the docs 
                0x805:"UNKNOWN_805",	# No name or docs, seems related to web query see #153260 for sample 
                0x810:"PIVOT_AUTOFORMAT",	# Seems to contain pivot table autoformat indicies, plus ?? 
                0x864:"UNKNOWN_864",	# seems related to pivot tables 
                0x867:"SHEETPROTECTION",	# OO named it, and has docs 
                0x868:"RANGEPROTECTION",	# OO named it, no docs yet 

                0x1001:"CHART_units",
                0x1002:"CHART_chart",
                0x1003:"CHART_series",
                0x1006:"CHART_dataformat",
                0x1007:"CHART_lineformat",
                0x1009:"CHART_markerformat",
                0x100a:"CHART_areaformat",
                0x100b:"CHART_pieformat",
                0x100c:"CHART_attachedlabel",
                0x100d:"CHART_seriestext",
                0x1014:"CHART_chartformat",
                0x1015:"CHART_legend",
                0x1016:"CHART_serieslist",
                0x1017:"CHART_bar",
                0x1018:"CHART_line",
                0x1019:"CHART_pie",
                0x101a:"CHART_area",
                0x101b:"CHART_scatter",
                0x101c:"CHART_chartline",
                0x101d:"CHART_axis",
                0x101e:"CHART_tick",
                0x101f:"CHART_valuerange",
                0x1020:"CHART_catserrange",
                0x1021:"CHART_axislineformat",
                0x1022:"CHART_chartformatlink",
                0x1024:"CHART_defaulttext",
                0x1025:"CHART_text",
                0x1026:"CHART_fontx",
                0x1027:"CHART_objectlink",
                0x1032:"CHART_frame",
                0x1033:"CHART_begin",
                0x1034:"CHART_end",
                0x1035:"CHART_plotarea",
                0x103a:"CHART_3d",
                0x103c:"CHART_picf",
                0x103d:"CHART_dropbar",
                0x103e:"CHART_radar",
                0x103f:"CHART_surf",
                0x1040:"CHART_radararea",
                0x1041:"CHART_axisparent",
                0x1043:"CHART_legendxn",
                0x1044:"CHART_shtprops",
                0x1045:"CHART_sertocrt",
                0x1046:"CHART_axesused",
                0x1048:"CHART_sbaseref",
                0x104a:"CHART_serparent",
                0x104b:"CHART_serauxtrend",
                0x104e:"CHART_ifmt",
                0x104f:"CHART_pos",
                0x1050:"CHART_alruns",
                0x1051:"CHART_ai",
                0x105b:"CHART_serauxerrbar",
                0x105c:"CHART_clrtclient",	# Undocumented 
                0x105d:"CHART_serfmt",
                0x105f:"CHART_3dbarshape",	# Undocumented 
                0x1060:"CHART_fbi",
                0x1061:"CHART_boppop",
                0x1062:"CHART_axcext",
                0x1063:"CHART_dat",
                0x1064:"CHART_plotgrowth",
                0x1065:"CHART_siindex",
                0x1066:"CHART_gelframe",
                0x1067:"CHART_boppopcustom",}
    class BIFF(FieldSet):
        def createFields(self):
            yield Enum(UInt16(self, "type"),ExcelWorkbook.BIFF_TYPES)
            yield UInt16(self, "length")
            if self["length"].value:
                yield RawBytes(self, "data", self["length"].value)
        def createDescription(self):
            return "Excel BIFF; type %s"%self["type"].display
    def createFields(self):
        pos=0
        while pos//8 < self.datasize:
            newobj=ExcelWorkbook.BIFF(self, "BIFF[]")
            yield newobj
            pos+=newobj.size

class ThumbsCatalog(OLE2FragmentParser):
    class ThumbsEntry(FieldSet):
        def createFields(self):
            yield UInt32(self, "size")
            yield UInt32(self, "index")
            yield Bits(self, "flags", 8)
            yield RawBytes(self, "unknown[]", 5)
            yield UInt16(self, "unknown[]")
            yield CString(self, "name", charset="UTF-16-LE")
            if self.current_size // 8 != self['size'].value:
                yield RawBytes(self, "padding", self['size'].value - self.current_size // 8)
        def createDescription(self):
            return "Thumbnail entry for %s"%self["name"].display

    def createFields(self):
        yield UInt16(self, "unknown[]")
        yield UInt16(self, "unknown[]")
        yield UInt32(self, "count")
        yield UInt32(self, "unknown[]")
        yield UInt32(self, "unknown[]")
        for i in xrange(self['count'].value):
            yield ThumbsCatalog.ThumbsEntry(self, "entry[]")

PROPERTY_NAME = {
    u"Root Entry": ("root",RootEntry),
    u"\5DocumentSummaryInformation": ("doc_summary",Summary),
    u"\5SummaryInformation": ("summary",Summary),
    u"\1CompObj": ("compobj",CompObj),
    u"Pictures": ("pictures",Pictures),
    u"PowerPoint Document": ("powerpointdoc",PowerPointDocument),
    u"Current User": ("current_user",CurrentUser),
    u"Workbook": ("workbook",ExcelWorkbook),
    u"Catalog": ("catalog",ThumbsCatalog),
    u"WordDocument": ("word_doc",WordDocumentParser),
    u"0Table": ("table0",WordTableParser),
    u"1Table": ("table1",WordTableParser),
}
