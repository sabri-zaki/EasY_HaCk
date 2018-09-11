from hachoir_core.endian import BIG_ENDIAN, LITTLE_ENDIAN
from hachoir_core.field import RawBytes, RootSeekableFieldSet, ParserError
from hachoir_parser import HachoirParser

class OLE2FragmentParser(HachoirParser,RootSeekableFieldSet):
    tags = {
        "description": "Microsoft Office document subfragments",
    }
    endian = LITTLE_ENDIAN

    ENDIAN_CHECK=False

    def __init__(self, stream, **args):
        RootSeekableFieldSet.__init__(self, None, "root", stream, None, stream.askSize(self))
        HachoirParser.__init__(self, stream, **args)
        if self.ENDIAN_CHECK:
            if self["endian"].value == "\xFF\xFE":
                self.endian = BIG_ENDIAN
            elif self["endian"].value == "\xFE\xFF":
                self.endian = LITTLE_ENDIAN
            else:
                raise ParserError("OLE2: Invalid endian value")

    def validate(self):
        if self.ENDIAN_CHECK:
            if self["endian"].value not in ["\xFF\xFE", "\xFE\xFF"]:
                return "Unknown endian value %s"%self["endian"].value.encode('hex')
        return True

class RawParser(OLE2FragmentParser):
    ENDIAN_CHECK=False
    OS_CHECK=False
    def createFields(self):
        yield RawBytes(self,"rawdata",self.datasize)
        if self.datasize<self.size//8: yield RawBytes(self,"slack_space",(self.size//8)-self.datasize)
