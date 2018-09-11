"""
JPEG picture parser.

Information:

- APP14 documents
  http://partners.adobe.com/public/developer/en/ps/sdk/5116.DCT_Filter.pdf
  http://java.sun.com/j2se/1.5.0/docs/api/javax/imageio/metadata/doc-files/jpeg_metadata.html#color
- APP12:
  http://search.cpan.org/~exiftool/Image-ExifTool/lib/Image/ExifTool/TagNames.pod
- JPEG Data Format
  http://www.w3.org/Graphics/JPEG/itu-t81.pdf

Author: Victor Stinner, Robert Xiao
"""

from hachoir_core.error import HachoirError
from hachoir_parser import Parser
from hachoir_core.field import (FieldSet, ParserError, FieldError,
    UInt8, UInt16, Enum, Field,
    Bit, Bits, NullBits, NullBytes, PaddingBits,
    String, RawBytes)
from hachoir_parser.image.common import PaletteRGB
from hachoir_core.endian import BIG_ENDIAN
from hachoir_core.text_handler import textHandler, hexadecimal
from hachoir_parser.image.exif import Exif
from hachoir_parser.image.photoshop_metadata import PhotoshopMetadata
from hachoir_parser.archive.zlib import build_tree
from hachoir_core.tools import paddingSize, alignValue

MAX_FILESIZE = 100 * 1024 * 1024

# The four tables (hash/sum for color/grayscale JPEG) comes
# from ImageMagick project
QUALITY_HASH_COLOR = (
    1020, 1015,  932,  848,  780,  735,  702,  679,  660,  645,
     632,  623,  613,  607,  600,  594,  589,  585,  581,  571,
     555,  542,  529,  514,  494,  474,  457,  439,  424,  410,
     397,  386,  373,  364,  351,  341,  334,  324,  317,  309,
     299,  294,  287,  279,  274,  267,  262,  257,  251,  247,
     243,  237,  232,  227,  222,  217,  213,  207,  202,  198,
     192,  188,  183,  177,  173,  168,  163,  157,  153,  148,
     143,  139,  132,  128,  125,  119,  115,  108,  104,   99,
      94,   90,   84,   79,   74,   70,   64,   59,   55,   49,
      45,   40,   34,   30,   25,   20,   15,   11,    6,    4,
       0)

QUALITY_SUM_COLOR = (
    32640,32635,32266,31495,30665,29804,29146,28599,28104,27670,
    27225,26725,26210,25716,25240,24789,24373,23946,23572,22846,
    21801,20842,19949,19121,18386,17651,16998,16349,15800,15247,
    14783,14321,13859,13535,13081,12702,12423,12056,11779,11513,
    11135,10955,10676,10392,10208, 9928, 9747, 9564, 9369, 9193,
     9017, 8822, 8639, 8458, 8270, 8084, 7896, 7710, 7527, 7347,
     7156, 6977, 6788, 6607, 6422, 6236, 6054, 5867, 5684, 5495,
     5305, 5128, 4945, 4751, 4638, 4442, 4248, 4065, 3888, 3698,
     3509, 3326, 3139, 2957, 2775, 2586, 2405, 2216, 2037, 1846,
     1666, 1483, 1297, 1109,  927,  735,  554,  375,  201,  128,
        0)

QUALITY_HASH_GRAY = (
    510,  505,  422,  380,  355,  338,  326,  318,  311,  305,
    300,  297,  293,  291,  288,  286,  284,  283,  281,  280,
    279,  278,  277,  273,  262,  251,  243,  233,  225,  218,
    211,  205,  198,  193,  186,  181,  177,  172,  168,  164,
    158,  156,  152,  148,  145,  142,  139,  136,  133,  131,
    129,  126,  123,  120,  118,  115,  113,  110,  107,  105,
    102,  100,   97,   94,   92,   89,   87,   83,   81,   79,
     76,   74,   70,   68,   66,   63,   61,   57,   55,   52,
     50,   48,   44,   42,   39,   37,   34,   31,   29,   26,
     24,   21,   18,   16,   13,   11,    8,    6,    3,    2,
      0)

QUALITY_SUM_GRAY = (
    16320,16315,15946,15277,14655,14073,13623,13230,12859,12560,
    12240,11861,11456,11081,10714,10360,10027, 9679, 9368, 9056,
     8680, 8331, 7995, 7668, 7376, 7084, 6823, 6562, 6345, 6125,
     5939, 5756, 5571, 5421, 5240, 5086, 4976, 4829, 4719, 4616,
     4463, 4393, 4280, 4166, 4092, 3980, 3909, 3835, 3755, 3688,
     3621, 3541, 3467, 3396, 3323, 3247, 3170, 3096, 3021, 2952,
     2874, 2804, 2727, 2657, 2583, 2509, 2437, 2362, 2290, 2211,
     2136, 2068, 1996, 1915, 1858, 1773, 1692, 1620, 1552, 1477,
     1398, 1326, 1251, 1179, 1109, 1031,  961,  884,  814,  736,
      667,  592,  518,  441,  369,  292,  221,  151,   86,   64,
        0)

JPEG_NATURAL_ORDER = (
     0,  1,  8, 16,  9,  2,  3, 10,
    17, 24, 32, 25, 18, 11,  4,  5,
    12, 19, 26, 33, 40, 48, 41, 34,
    27, 20, 13,  6,  7, 14, 21, 28,
    35, 42, 49, 56, 57, 50, 43, 36,
    29, 22, 15, 23, 30, 37, 44, 51,
    58, 59, 52, 45, 38, 31, 39, 46,
    53, 60, 61, 54, 47, 55, 62, 63)

class JpegChunkApp0(FieldSet):
    UNIT_NAME = {
        0: "pixels",
        1: "dots per inch",
        2: "dots per cm",
    }

    def createFields(self):
        yield String(self, "jfif", 5, "JFIF string", charset="ASCII")
        if self["jfif"].value != "JFIF\0":
            raise ParserError(
                "Stream doesn't look like JPEG chunk (wrong JFIF signature)")
        yield UInt8(self, "ver_maj", "Major version")
        yield UInt8(self, "ver_min", "Minor version")
        yield Enum(UInt8(self, "units", "Units"), self.UNIT_NAME)
        if self["units"].value == 0:
            yield UInt16(self, "aspect_x", "Aspect ratio (X)")
            yield UInt16(self, "aspect_y", "Aspect ratio (Y)")
        else:
            yield UInt16(self, "x_density", "X density")
            yield UInt16(self, "y_density", "Y density")
        yield UInt8(self, "thumb_w", "Thumbnail width")
        yield UInt8(self, "thumb_h", "Thumbnail height")
        thumb_size = self["thumb_w"].value * self["thumb_h"].value
        if thumb_size != 0:
            yield PaletteRGB(self, "thumb_palette", 256)
            yield RawBytes(self, "thumb_data", thumb_size, "Thumbnail data")

class Ducky(FieldSet):
    BLOCK_TYPE = {
        0: "end",
        1: "Quality",
        2: "Comment",
        3: "Copyright",
    }
    def createFields(self):
        yield Enum(UInt16(self, "type"), self.BLOCK_TYPE)
        if self["type"].value == 0:
            return
        yield UInt16(self, "size")
        size = self["size"].value
        if size:
            yield RawBytes(self, "data", size)

class APP12(FieldSet):
    """
    The JPEG APP12 "Picture Info" segment was used by some older cameras, and
    contains ASCII-based meta information.
    """
    def createFields(self):
        yield String(self, "ducky", 5, '"Ducky" string', charset="ASCII")
        while not self.eof:
            yield Ducky(self, "item[]")

class SOFComponent(FieldSet):
    def createFields(self):
        yield UInt8(self, "component_id")
        yield Bits(self, "horiz_sample", 4, "Horizontal sampling factor")
        yield Bits(self, "vert_sample", 4, "Vertical sampling factor")
        yield UInt8(self, "quant_table", "Quantization table destination selector")

class StartOfFrame(FieldSet):
    def createFields(self):
        yield UInt8(self, "precision")

        yield UInt16(self, "height")
        yield UInt16(self, "width")
        yield UInt8(self, "nr_components")

        for index in range(self["nr_components"].value):
            yield SOFComponent(self, "component[]")

class Comment(FieldSet):
    def createFields(self):
        yield String(self, "comment", self.size//8, strip="\0")

class AdobeChunk(FieldSet):
    COLORSPACE_TRANSFORMATION = {
        1: "YCbCr (converted from RGB)",
        2: "YCCK (converted from CMYK)",
    }
    def createFields(self):
        if self.stream.readBytes(self.absolute_address, 5) != "Adobe":
            yield RawBytes(self, "raw", self.size//8, "Raw data")
            return
        yield String(self, "adobe", 5, "\"Adobe\" string", charset="ASCII")
        yield UInt16(self, "version", "DCT encoder version")
        yield Enum(Bit(self, "flag00"),
            {False: "Chop down or subsampling", True: "Blend"})
        yield NullBits(self, "flags0_reserved", 15)
        yield NullBytes(self, "flags1", 2)
        yield Enum(UInt8(self, "color_transform", "Colorspace transformation code"), self.COLORSPACE_TRANSFORMATION)

class SOSComponent(FieldSet):
    def createFields(self):
        comp_id = UInt8(self, "component_id")
        yield comp_id
        if not(1 <= comp_id.value <= self["../nr_components"].value):
           raise ParserError("JPEG error: Invalid component-id")
        yield Bits(self, "dc_coding_table", 4, "DC entropy coding table destination selector")
        yield Bits(self, "ac_coding_table", 4, "AC entropy coding table destination selector")

class StartOfScan(FieldSet):
    def createFields(self):
        yield UInt8(self, "nr_components")

        for index in range(self["nr_components"].value):
            yield SOSComponent(self, "component[]")
        yield UInt8(self, "spectral_start", "Start of spectral or predictor selection")
        yield UInt8(self, "spectral_end", "End of spectral selection")
        yield Bits(self, "bit_pos_high", 4, "Successive approximation bit position high")
        yield Bits(self, "bit_pos_low", 4, "Successive approximation bit position low or point transform")

class RestartInterval(FieldSet):
    def createFields(self):
        yield UInt16(self, "interval", "Restart interval")

class QuantizationTable(FieldSet):
    def createFields(self):
        # Code based on function get_dqt() (jdmarker.c from libjpeg62)
        yield Bits(self, "is_16bit", 4)
        yield Bits(self, "index", 4)
        if self["index"].value >= 4:
            raise ParserError("Invalid quantification index (%s)" % self["index"].value)
        if self["is_16bit"].value:
            coeff_type = UInt16
        else:
            coeff_type = UInt8
        for index in xrange(64):
            natural = JPEG_NATURAL_ORDER[index]
            yield coeff_type(self, "coeff[%u]" % natural)

    def createDescription(self):
        return "Quantification table #%u" % self["index"].value

class DefineQuantizationTable(FieldSet):
    def createFields(self):
        while self.current_size < self.size:
            yield QuantizationTable(self, "qt[]")

class HuffmanTable(FieldSet):
    def createFields(self):
        # http://www.w3.org/Graphics/JPEG/itu-t81.pdf, page 40-41
        yield Enum(Bits(self, "table_class", 4, "Table class"), {
            0:"DC or Lossless Table",
            1:"AC Table"})
        yield Bits(self, "index", 4, "Huffman table destination identifier")
        for i in xrange(1, 17):
            yield UInt8(self, "count[%i]" % i, "Number of codes of length %i" % i)
        lengths = []
        remap = {}
        for i in xrange(1, 17):
            for j in xrange(self["count[%i]" % i].value):
                field = UInt8(self, "value[%i][%i]" % (i, j), "Value of code #%i of length %i" % (j, i))
                yield field
                remap[len(lengths)] = field.value
                lengths.append(i)
        self.tree = {}
        for i,j in build_tree(lengths).iteritems():
            self.tree[i] = remap[j]

class DefineHuffmanTable(FieldSet):
    def createFields(self):
        while self.current_size < self.size:
            yield HuffmanTable(self, "huffman_table[]")

class HuffmanCode(Field):
    """Huffman code. Uses tree parameter as the Huffman tree."""
    def __init__(self, parent, name, tree, description=""):
        Field.__init__(self, parent, name, 0, description)

        endian = self.parent.endian
        stream = self.parent.stream
        addr = self.absolute_address

        value = 0
        met_ff = False
        while (self.size, value) not in tree:
            if addr % 8 == 0:
                last_byte = stream.readBytes(addr - 8, 1)
                if last_byte == '\xFF':
                    next_byte = stream.readBytes(addr, 1)
                    if next_byte != '\x00':
                        raise FieldError("Unexpected byte sequence %r!"%(last_byte + next_byte))
                    addr += 8 # hack hack hack
                    met_ff = True
                    self._description = "[skipped 8 bits after 0xFF] "
            bit = stream.readBits(addr, 1, endian)
            value <<= 1
            value += bit
            self._size += 1
            addr += 1
        self.createValue = lambda: value
        self.realvalue = tree[(self.size, value)]
        if met_ff:
            self._size += 8

class JpegHuffmanImageUnit(FieldSet):
    """8x8 block of sample/coefficient values"""
    def __init__(self, parent, name, dc_tree, ac_tree, *args, **kwargs):
        FieldSet.__init__(self, parent, name, *args, **kwargs)
        self.dc_tree = dc_tree
        self.ac_tree = ac_tree

    def createFields(self):
        field = HuffmanCode(self, "dc_data", self.dc_tree)
        field._description = "DC Code %i (Huffman Code %i)" % (field.realvalue, field.value) + field._description
        yield field
        if field.realvalue != 0:
            extra = Bits(self, "dc_data_extra", field.realvalue)
            if extra.value < 2**(field.realvalue - 1):
                corrected_value = extra.value + (-1 << field.realvalue) + 1
            else:
                corrected_value = extra.value
            extra._description = "Extra Bits: Corrected DC Value %i" % corrected_value
            yield extra
        data = []
        while len(data) < 63:
            field = HuffmanCode(self, "ac_data[]", self.ac_tree)
            value_r = field.realvalue >> 4
            if value_r:
                data += [0] * value_r
            value_s = field.realvalue & 0x0F
            if value_r == value_s == 0:
                field._description = "AC Code Block Terminator (0, 0) (Huffman Code %i)" % field.value + field._description
                yield field
                return
            field._description = "AC Code %i, %i (Huffman Code %i)" % (value_r, value_s, field.value) + field._description
            yield field
            if value_s != 0:
                extra = Bits(self, "ac_data_extra[%s" % field.name.split('[')[1], value_s)
                if extra.value < 2**(value_s - 1):
                    corrected_value = extra.value + (-1 << value_s) + 1
                else:
                    corrected_value = extra.value
                extra._description = "Extra Bits: Corrected AC Value %i" % corrected_value
                data.append(corrected_value)
                yield extra
            else:
                data.append(0)

class JpegImageData(FieldSet):
    def __init__(self, parent, name, frame, scan, restart_interval, restart_offset=0, *args, **kwargs):
        FieldSet.__init__(self, parent, name, *args, **kwargs)
        self.frame = frame
        self.scan = scan
        self.restart_interval = restart_interval
        self.restart_offset = restart_offset
        # try to figure out where this field ends
        start = self.absolute_address
        while True:
            end = self.stream.searchBytes("\xff", start, MAX_FILESIZE*8)
            if end is None:
                # this is a bad sign, since it means there is no terminator
                # we ignore this; it likely means a truncated image
                break
            if self.stream.readBytes(end, 2) == '\xff\x00':
                # padding: false alarm
                start=end+16
                continue
            else:
                self._size = end-self.absolute_address
                break

    def createFields(self):
        if self.frame["../type"].value in [0xC0, 0xC1]:
            # yay, huffman coding!
            if not hasattr(self, "huffman_tables"):
                self.huffman_tables = {}
                for huffman in self.parent.array("huffman"):
                    for table in huffman["content"].array("huffman_table"):
                        for _dummy_ in table:
                            # exhaust table, so the huffman tree is built
                            pass
                        self.huffman_tables[table["table_class"].value, table["index"].value] = table.tree
            components = [] # sos_comp, samples
            max_vert = 0
            max_horiz = 0
            for component in self.scan.array("component"):
                for sof_comp in self.frame.array("component"):
                    if sof_comp["component_id"].value == component["component_id"].value:
                        vert = sof_comp["vert_sample"].value
                        horiz = sof_comp["horiz_sample"].value
                        components.append((component, vert * horiz))
                        max_vert = max(max_vert, vert)
                        max_horiz = max(max_horiz, horiz)
            mcu_height = alignValue(self.frame["height"].value, 8 * max_vert) // (8 * max_vert)
            mcu_width = alignValue(self.frame["width"].value, 8 * max_horiz) // (8 * max_horiz)
            if self.restart_interval and self.restart_offset > 0:
                mcu_number = self.restart_interval * self.restart_offset
            else:
                mcu_number = 0
            initial_mcu = mcu_number
            while True:
                if (self.restart_interval and mcu_number != initial_mcu and mcu_number % self.restart_interval == 0) or\
                   mcu_number == mcu_height * mcu_width:
                    padding = paddingSize(self.current_size, 8)
                    if padding:
                        yield PaddingBits(self, "padding[]", padding) # all 1s
                    last_byte = self.stream.readBytes(self.absolute_address + self.current_size - 8, 1)
                    if last_byte == '\xFF':
                        next_byte = self.stream.readBytes(self.absolute_address + self.current_size, 1)
                        if next_byte != '\x00':
                            raise FieldError("Unexpected byte sequence %r!"%(last_byte + next_byte))
                        yield NullBytes(self, "stuffed_byte[]", 1)
                    break
                for sos_comp, num_units in components:
                    for interleave_count in range(num_units):
                        yield JpegHuffmanImageUnit(self, "block[%i]component[%i][]" % (mcu_number, sos_comp["component_id"].value),
                                              self.huffman_tables[0, sos_comp["dc_coding_table"].value],
                                              self.huffman_tables[1, sos_comp["ac_coding_table"].value])
                mcu_number += 1
        else:
            self.warning("Sorry, only supporting Baseline & Extended Sequential JPEG images so far!")
            return

class JpegChunk(FieldSet):
    TAG_SOI = 0xD8
    TAG_EOI = 0xD9
    TAG_SOS = 0xDA
    TAG_DQT = 0xDB
    TAG_DRI = 0xDD
    TAG_INFO = {
        0xC4: ("huffman[]", "Define Huffman Table (DHT)", DefineHuffmanTable),
        0xD8: ("start_image", "Start of image (SOI)", None),
        0xD9: ("end_image", "End of image (EOI)", None),
        0xD0: ("restart_marker_0[]", "Restart Marker (RST0)", None),
        0xD1: ("restart_marker_1[]", "Restart Marker (RST1)", None),
        0xD2: ("restart_marker_2[]", "Restart Marker (RST2)", None),
        0xD3: ("restart_marker_3[]", "Restart Marker (RST3)", None),
        0xD4: ("restart_marker_4[]", "Restart Marker (RST4)", None),
        0xD5: ("restart_marker_5[]", "Restart Marker (RST5)", None),
        0xD6: ("restart_marker_6[]", "Restart Marker (RST6)", None),
        0xD7: ("restart_marker_7[]", "Restart Marker (RST7)", None),
        0xDA: ("start_scan[]", "Start Of Scan (SOS)", StartOfScan),
        0xDB: ("quantization[]", "Define Quantization Table (DQT)", DefineQuantizationTable),
        0xDC: ("nb_line", "Define number of Lines (DNL)", None),
        0xDD: ("restart_interval", "Define Restart Interval (DRI)", RestartInterval),
        0xE0: ("app0", "APP0", JpegChunkApp0),
        0xE1: ("exif", "Exif metadata", Exif),
        0xE2: ("icc", "ICC profile", None),
        0xEC: ("app12", "APP12", APP12),
        0xED: ("photoshop", "Photoshop", PhotoshopMetadata),
        0xEE: ("adobe", "Image encoding information for DCT filters (Adobe)", AdobeChunk),
        0xFE: ("comment[]", "Comment", Comment),
    }
    START_OF_FRAME = {
        0xC0: u"Baseline",
        0xC1: u"Extended sequential",
        0xC2: u"Progressive",
        0xC3: u"Lossless",
        0xC5: u"Differential sequential",
        0xC6: u"Differential progressive",
        0xC7: u"Differential lossless",
        0xC9: u"Extended sequential, arithmetic coding",
        0xCA: u"Progressive, arithmetic coding",
        0xCB: u"Lossless, arithmetic coding",
        0xCD: u"Differential sequential, arithmetic coding",
        0xCE: u"Differential progressive, arithmetic coding",
        0xCF: u"Differential lossless, arithmetic coding",
    }
    for key, text in START_OF_FRAME.iteritems():
        TAG_INFO[key] = ("start_frame", "Start of frame (%s)" % text.lower(), StartOfFrame)

    def __init__(self, parent, name, description=None):
        FieldSet.__init__(self, parent, name, description)
        tag = self["type"].value
        if tag == 0xE1:
            # Hack for Adobe extension: XAP metadata (as XML)
            bytes = self.stream.readBytes(self.absolute_address + 32, 6)
            if bytes == "Exif\0\0":
                self._name = "exif"
                self._description = "EXIF"
                self._parser = Exif
            else:
                self._parser = None
        elif tag in self.TAG_INFO:
            self._name, self._description, self._parser = self.TAG_INFO[tag]
        else:
            self._parser = None

    def createFields(self):
        yield textHandler(UInt8(self, "header", "Header"), hexadecimal)
        if self["header"].value != 0xFF:
            raise ParserError("JPEG: Invalid chunk header!")
        yield textHandler(UInt8(self, "type", "Type"), hexadecimal)
        tag = self["type"].value
        if tag in [self.TAG_SOI, self.TAG_EOI] + range(0xD0, 0xD8): # D0 - D7 inclusive are the restart markers
            return
        yield UInt16(self, "size", "Size")
        size = (self["size"].value - 2)
        if 0 < size:
            if self._parser:
                yield self._parser(self, "content", "Chunk content", size=size*8)
            else:
                yield RawBytes(self, "data", size, "Data")

    def createDescription(self):
        return "Chunk: %s" % self["type"].display

class JpegFile(Parser):
    endian = BIG_ENDIAN
    PARSER_TAGS = {
        "id": "jpeg",
        "category": "image",
        "file_ext": ("jpg", "jpeg"),
        "mime": (u"image/jpeg",),
        "magic": (
            ("\xFF\xD8\xFF\xE0", 0),   # (Start Of Image, APP0)
            ("\xFF\xD8\xFF\xE1", 0),   # (Start Of Image, EXIF)
            ("\xFF\xD8\xFF\xEE", 0),   # (Start Of Image, Adobe)
        ),
        "min_size": 22*8,
        "description": "JPEG picture",
        "subfile": "skip",
    }

    def validate(self):
        if self.stream.readBytes(0, 2) != "\xFF\xD8":
            return "Invalid file signature"
        try:
            for index, field in enumerate(self):
                chunk_type = field["type"].value
                if chunk_type not in JpegChunk.TAG_INFO:
                    return "Unknown chunk type: 0x%02X (chunk #%s)" % (chunk_type, index)
                if index == 2:
                    # Only check 3 fields
                    break
        except HachoirError:
            return "Unable to parse at least three chunks"
        return True

    def createFields(self):
        frame = None
        scan = None
        restart_interval = None
        restart_offset = 0
        while not self.eof:
            chunk = JpegChunk(self, "chunk[]")
            yield chunk
            if chunk["type"].value in JpegChunk.START_OF_FRAME:
                if chunk["type"].value not in [0xC0, 0xC1]: # SOF0 [Baseline], SOF1 [Extended Sequential]
                    self.warning("Only supporting Baseline & Extended Sequential JPEG images so far!")
                frame = chunk["content"]
            if chunk["type"].value == JpegChunk.TAG_SOS:
                if not frame:
                    self.warning("Missing or invalid SOF marker before SOS!")
                    continue
                scan = chunk["content"]
                # hack: scan only the fields seen so far (in _fields): don't use the generator
                if "restart_interval" in self._fields:
                    restart_interval = self["restart_interval/content/interval"].value
                else:
                    restart_interval = None
                yield JpegImageData(self, "image_data[]", frame, scan, restart_interval)
            elif chunk["type"].value in range(0xD0, 0xD8):
                restart_offset += 1
                yield JpegImageData(self, "image_data[]", frame, scan, restart_interval, restart_offset)

        # TODO: is it possible to handle piped input?
        if self._size is None:
            raise NotImplementedError

        has_end = False
        size = (self._size - self.current_size) // 8
        if size:
            if 2 < size \
            and self.stream.readBytes(self._size - 16, 2) == "\xff\xd9":
                has_end = True
                size -= 2
            yield RawBytes(self, "data", size, "JPEG data")
        if has_end:
            yield JpegChunk(self, "chunk[]")

    def createDescription(self):
        desc = "JPEG picture"
        if "start_frame/content" in self:
            header = self["start_frame/content"]
            desc += ": %ux%u pixels" % (header["width"].value, header["height"].value)
        return desc

    def createContentSize(self):
        if "end" in self:
            return self["end"].absolute_address + self["end"].size
        if "data" not in self:
            return None
        start = self["data"].absolute_address
        end = self.stream.searchBytes("\xff\xd9", start, MAX_FILESIZE*8)
        if end is not None:
            return end + 16
        return None
