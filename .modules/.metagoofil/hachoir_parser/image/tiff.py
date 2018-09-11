"""
TIFF image parser.

Authors: Victor Stinner, Sebastien Ponce, Robert Xiao
Creation date: 30 september 2006
"""

from hachoir_parser import Parser
from hachoir_core.field import FieldSet, SeekableFieldSet, RootSeekableFieldSet, Bytes
from hachoir_core.endian import LITTLE_ENDIAN, BIG_ENDIAN
from hachoir_parser.image.exif import TIFF

def getStrips(ifd):
    data = {}
    for i, entry in enumerate(ifd.array('entry')):
        data[entry['tag'].display] = entry
    # image data
    if "StripOffsets" in data and "StripByteCounts" in data:
        offs = ifd.getEntryValues(data["StripOffsets"])
        bytes = ifd.getEntryValues(data["StripByteCounts"])
        for off, byte in zip(offs, bytes):
            yield off.value, byte.value

class ImageFile(SeekableFieldSet):
    def __init__(self, parent, name, description, ifd):
        SeekableFieldSet.__init__(self, parent, name, description, None)
        self._ifd = ifd

    def createFields(self):
        for off, byte in getStrips(self._ifd):
            self.seekByte(off, relative=False)
            yield Bytes(self, "strip[]", byte)

class TiffFile(RootSeekableFieldSet, Parser):
    PARSER_TAGS = {
        "id": "tiff",
        "category": "image",
        "file_ext": ("tif", "tiff"),
        "mime": (u"image/tiff",),
        "min_size": 8*8,
        "magic": (("II\x2A\0", 0), ("MM\0\x2A", 0)),
        "description": "TIFF picture"
    }

    # Correct endian is set in constructor
    endian = LITTLE_ENDIAN

    def __init__(self, stream, **args):
        RootSeekableFieldSet.__init__(self, None, "root", stream, None, stream.askSize(self))
        if self.stream.readBytes(0, 2) == "MM":
            self.endian = BIG_ENDIAN
        Parser.__init__(self, stream, **args)

    def validate(self):
        endian = self.stream.readBytes(0, 2)
        if endian not in ("MM", "II"):
            return "Invalid endian (%r)" % endian
        if self["version"].value != 42:
            return "Unknown TIFF version"
        return True

    def createFields(self):
        for field in TIFF(self):
            yield field

        for ifd in self.array('ifd'):
            offs = (off for off, byte in getStrips(ifd))
            self.seekByte(min(offs), relative=False)
            image = ImageFile(self, "image[]", "Image File", ifd)
            yield image
