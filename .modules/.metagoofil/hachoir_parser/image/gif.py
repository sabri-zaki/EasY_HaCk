"""
GIF picture parser.

Author: Victor Stinner, Robert Xiao

- GIF format
  http://local.wasp.uwa.edu.au/~pbourke/dataformats/gif/
- LZW compression
  http://en.wikipedia.org/wiki/LZW
"""

from hachoir_parser import Parser
from hachoir_core.field import (FieldSet, ParserError,
    Enum, UInt8, UInt16,
    Bit, Bits, NullBytes,
    String, PascalString8, Character,
    NullBits, RawBytes)
from hachoir_parser.image.common import PaletteRGB
from hachoir_core.endian import LITTLE_ENDIAN
from hachoir_core.stream import StringInputStream
from hachoir_core.tools import humanDuration, paddingSize
from hachoir_core.text_handler import textHandler, displayHandler, hexadecimal

# Maximum image dimension (in pixel)
MAX_WIDTH = 6000
MAX_HEIGHT = MAX_WIDTH
MAX_FILE_SIZE = 100 * 1024 * 1024

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
        self.args["startbits"] = self.items[0].parent["lzw_min_code_size"].value
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
        yield UInt8(self, "size")
        yield RawBytes(self, "rawdata", self["size"].value)

    def _createInputStream(self, **args):
        return self.group.createInputStream()

def rle_repr(l):
    """Run-length encode a list into an "eval"-able form

    Example:
    >>> rle_repr([20, 16, 16, 16, 16, 16, 18, 18, 65])
    '[20] + [16]*5 + [18]*2 + [65]'

    Adapted from http://twistedmatrix.com/trac/browser/trunk/twisted/python/dxprofile.py
    """
    def add_rle(previous, runlen, result):
        if isinstance(previous, (list, tuple)):
            previous = rle_repr(previous)
        if runlen>1:
            result.append('[%s]*%i'%(previous, runlen))
        else:
            if result and '*' not in result[-1]:
                result[-1] = '[%s, %s]'%(result[-1][1:-1], previous)
            else:
                result.append('[%s]'%previous)
    iterable = iter(l)
    runlen = 1
    result = []
    try:
        previous = iterable.next()
    except StopIteration:
        return "[]"
    for element in iterable:
        if element == previous:
            runlen = runlen + 1
            continue
        else:
            add_rle(previous, runlen, result)
            previous = element
            runlen = 1
    add_rle(previous, runlen, result)
    return ' + '.join(result)

class GifImageBlock(Parser):
    endian = LITTLE_ENDIAN
    def createFields(self):
        dictionary = {}
        self.nbits = self.startbits
        CLEAR_CODE = 2**self.nbits
        END_CODE = CLEAR_CODE + 1
        compress_code = CLEAR_CODE + 2
        obuf = []
        output = []
        while True:
            if compress_code >= 2**self.nbits:
                self.nbits += 1
            code = Bits(self, "code[]", self.nbits)
            if code.value == CLEAR_CODE:
                if compress_code == 2**(self.nbits-1):
                    # this fixes a bizarre edge case where the reset code could
                    # appear just after the bits incremented. Apparently, the
                    # correct behaviour is to express the reset code with the
                    # old number of bits, not the new...
                    code = Bits(self, "code[]", self.nbits-1)
                self.nbits = self.startbits + 1
                dictionary = {}
                compress_code = CLEAR_CODE + 2
                obuf = []
                code._description = "Reset Code (LZW code %i)" % code.value
                yield code
                continue
            elif code.value == END_CODE:
                code._description = "End of Information Code (LZW code %i)" % code.value
                yield code
                break
            if code.value < CLEAR_CODE: # literal
                if obuf:
                    chain = obuf + [code.value]
                    dictionary[compress_code] = chain
                    compress_code += 1
                obuf = [code.value]
                output.append(code.value)
                code._description = "Literal Code %i" % code.value
            elif code.value >= CLEAR_CODE + 2:
                if code.value in dictionary:
                    chain = dictionary[code.value]
                    code._description = "Compression Code %i (found in dictionary as %s)" % (code.value, rle_repr(chain))
                else:
                    chain = obuf + [obuf[0]]
                    code._description = "Compression Code %i (not found in dictionary; guessed to be %s)" % (code.value, rle_repr(chain))
                dictionary[compress_code] = obuf + [chain[0]]
                compress_code += 1
                obuf = chain
                output += chain
            code._description += "; Current Decoded Length %i"%len(output)
            yield code
        padding = paddingSize(self.current_size, 8)
        if padding:
            yield NullBits(self, "padding[]", padding)

class Image(FieldSet):
    def createFields(self):
        yield UInt16(self, "left", "Left")
        yield UInt16(self, "top", "Top")
        yield UInt16(self, "width", "Width")
        yield UInt16(self, "height", "Height")

        yield Bits(self, "size_local_map", 3, "log2(size of local map) minus one")
        yield NullBits(self, "reserved", 2)
        yield Bit(self, "sort_flag", "Is the local map sorted by decreasing importance?")
        yield Bit(self, "interlaced", "Interlaced?")
        yield Bit(self, "has_local_map", "Use local color map?")

        if self["has_local_map"].value:
            nb_color = 1 << (1 + self["size_local_map"].value)
            yield PaletteRGB(self, "local_map", nb_color, "Local color map")

        yield UInt8(self, "lzw_min_code_size", "LZW Minimum Code Size")
        group = None
        while True:
            size = UInt8(self, "block_size")
            if size.value == 0:
                break
            block = CustomFragment(self, "image_block[]", None, GifImageBlock, "GIF Image Block", group)
            group = block.group
            yield block
        yield NullBytes(self, "terminator", 1, "Terminator (0)")

    def createDescription(self):
        return "Image: %ux%u pixels at (%u,%u)" % (
            self["width"].value, self["height"].value,
            self["left"].value, self["top"].value)

DISPOSAL_METHOD = {
    0: "No disposal specified",
    1: "Do not dispose",
    2: "Restore to background color",
    3: "Restore to previous",
}

NETSCAPE_CODE = {
    1: "Loop count",
}

def parseApplicationExtension(parent):
    yield PascalString8(parent, "app_name", "Application name")
    while True:
        size = UInt8(parent, "size[]")
        if size.value == 0:
            break
        yield size
        if parent["app_name"].value == "NETSCAPE2.0" and size.value == 3:
            yield Enum(UInt8(parent, "netscape_code"), NETSCAPE_CODE)
            if parent["netscape_code"].value == 1:
                yield UInt16(parent, "loop_count")
            else:
                yield RawBytes(parent, "raw[]", 2)
        else:
            yield RawBytes(parent, "raw[]", size.value)
    yield NullBytes(parent, "terminator", 1, "Terminator (0)")

def parseGraphicControl(parent):
    yield UInt8(parent, "size", "Block size (4)")

    yield Bit(parent, "has_transp", "Has transparency")
    yield Bit(parent, "user_input", "User input")
    yield Enum(Bits(parent, "disposal_method", 3), DISPOSAL_METHOD)
    yield NullBits(parent, "reserved[]", 3)

    if parent["size"].value != 4:
        raise ParserError("Invalid graphic control size")
    yield displayHandler(UInt16(parent, "delay", "Delay time in millisecond"), humanDuration)
    yield UInt8(parent, "transp", "Transparent color index")
    yield NullBytes(parent, "terminator", 1, "Terminator (0)")

def parseComments(parent):
    while True:
        field = PascalString8(parent, "comment[]", strip=" \0\r\n\t")
        yield field
        if field.length == 0:
            break

def parseTextExtension(parent):
    yield UInt8(parent, "block_size", "Block Size")
    yield UInt16(parent, "left", "Text Grid Left")
    yield UInt16(parent, "top", "Text Grid Top")
    yield UInt16(parent, "width", "Text Grid Width")
    yield UInt16(parent, "height", "Text Grid Height")
    yield UInt8(parent, "cell_width", "Character Cell Width")
    yield UInt8(parent, "cell_height", "Character Cell Height")
    yield UInt8(parent, "fg_color", "Foreground Color Index")
    yield UInt8(parent, "bg_color", "Background Color Index")
    while True:
        field = PascalString8(parent, "comment[]", strip=" \0\r\n\t")
        yield field
        if field.length == 0:
            break

def defaultExtensionParser(parent):
    while True:
        size = UInt8(parent, "size[]", "Size (in bytes)")
        yield size
        if 0 < size.value:
            yield RawBytes(parent, "content[]", size.value)
        else:
            break

class Extension(FieldSet):
    ext_code = {
        0xf9: ("graphic_ctl[]", parseGraphicControl, "Graphic control"),
        0xfe: ("comments[]", parseComments, "Comments"),
        0xff: ("app_ext[]", parseApplicationExtension, "Application extension"),
        0x01: ("text_ext[]", parseTextExtension, "Plain text extension")
    }
    def __init__(self, *args):
        FieldSet.__init__(self, *args)
        code = self["code"].value
        if code in self.ext_code:
            self._name, self.parser, self._description = self.ext_code[code]
        else:
            self.parser = defaultExtensionParser

    def createFields(self):
        yield textHandler(UInt8(self, "code", "Extension code"), hexadecimal)
        for field in self.parser(self):
            yield field

    def createDescription(self):
        return "Extension: function %s" % self["func"].display

class ScreenDescriptor(FieldSet):
    def createFields(self):
        yield UInt16(self, "width", "Width")
        yield UInt16(self, "height", "Height")
        yield Bits(self, "size_global_map", 3, "log2(size of global map) minus one")
        yield Bit(self, "sort_flag", "Is the global map sorted by decreasing importance?")
        yield Bits(self, "color_res", 3, "Color resolution minus one")
        yield Bit(self, "global_map", "Has global map?")
        yield UInt8(self, "background", "Background color")
        field = UInt8(self, "pixel_aspect_ratio")
        if field.value:
            field._description = "Pixel aspect ratio: %f (stored as %i)"%((field.value + 15)/64., field.value)
        else:
            field._description = "Pixel aspect ratio: not specified"
        yield field

    def createDescription(self):
        colors = 1 << (self["size_global_map"].value+1)
        return "Screen descriptor: %ux%u pixels %u colors" \
            % (self["width"].value, self["height"].value, colors)

class GifFile(Parser):
    endian = LITTLE_ENDIAN
    separator_name = {
        "!": "Extension",
        ",": "Image",
        ";": "Terminator"
    }
    PARSER_TAGS = {
        "id": "gif",
        "category": "image",
        "file_ext": ("gif",),
        "mime": (u"image/gif",),
        "min_size": (6 + 7 + 1 + 9)*8,   # signature + screen + separator + image
        "magic": (("GIF87a", 0), ("GIF89a", 0)),
        "description": "GIF picture"
    }

    def validate(self):
        if self.stream.readBytes(0, 6) not in ("GIF87a", "GIF89a"):
            return "Wrong header"
        if self["screen/width"].value == 0 or self["screen/height"].value == 0:
            return "Invalid image size"
        if MAX_WIDTH < self["screen/width"].value:
            return "Image width too big (%u)" % self["screen/width"].value
        if MAX_HEIGHT < self["screen/height"].value:
            return "Image height too big (%u)" % self["screen/height"].value
        return True

    def createFields(self):
        # Header
        yield String(self, "magic", 3, "File magic code", charset="ASCII")
        yield String(self, "version", 3, "GIF version", charset="ASCII")

        yield ScreenDescriptor(self, "screen")
        if self["screen/global_map"].value:
            bpp = (self["screen/size_global_map"].value+1)
            yield PaletteRGB(self, "color_map", 1 << bpp, "Color map")
            self.color_map = self["color_map"]
        else:
            self.color_map = None

        self.images = []
        while True:
            code = Enum(Character(self, "separator[]", "Separator code"), self.separator_name)
            yield code
            code = code.value
            if code == "!":
                yield Extension(self, "extensions[]")
            elif code == ",":
                yield Image(self, "image[]")
            elif code == ";":
                # GIF Terminator
                break
            else:
                raise ParserError("Wrong GIF image separator: 0x%02X" % ord(code))

    def createContentSize(self):
        field = self["image[0]"]
        start = field.absolute_address + field.size
        end = start + MAX_FILE_SIZE*8
        pos = self.stream.searchBytes("\0;", start, end)
        if pos:
            return pos + 16
        return None
