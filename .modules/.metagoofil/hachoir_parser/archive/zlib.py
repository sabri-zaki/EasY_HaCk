"""Detailed ZLIB parser

Author: Robert Xiao
Creation date: July 9 2007

"""

from hachoir_parser import Parser
from hachoir_core.field import (Bit, Bits, Field, Int16, UInt32,
    Enum, FieldSet, GenericFieldSet,
    PaddingBits, ParserError, RawBytes)
from hachoir_core.endian import LITTLE_ENDIAN
from hachoir_core.text_handler import textHandler, hexadecimal
from hachoir_core.tools import paddingSize, alignValue

def extend_data(data, length, offset):
    """Extend data using a length and an offset."""
    if length >= offset:
        new_data = data[-offset:] * (alignValue(length, offset) // offset)
        return data + new_data[:length]
    else:
        return data + data[-offset:-offset+length]

def build_tree(lengths):
    """Build a Huffman tree from a list of lengths.
       The ith entry of the input list is the length of the Huffman code corresponding to
       integer i, or 0 if the integer i is unused."""
    max_length = max(lengths) + 1
    bit_counts = [0]*max_length
    next_code = [0]*max_length
    tree = {}
    for i in lengths:
        if i:
            bit_counts[i] += 1
    code = 0
    for i in xrange(1, len(bit_counts)):
        next_code[i] = code = (code + bit_counts[i-1]) << 1
    for i, ln in enumerate(lengths):
        if ln:
            tree[(ln, next_code[ln])] = i
            next_code[ln] += 1
    return tree

class HuffmanCode(Field):
    """Huffman code. Uses tree parameter as the Huffman tree."""
    def __init__(self, parent, name, tree, description=None):
        Field.__init__(self, parent, name, 0, description)

        endian = self.parent.endian
        stream = self.parent.stream
        addr = self.absolute_address

        value = 0
        while (self.size, value) not in tree:
            if self.size > 256:
                raise ParserError("Huffman code too long!")
            bit = stream.readBits(addr, 1, endian)
            value <<= 1
            value += bit
            self._size += 1
            addr += 1
        self.huffvalue = value
        self.realvalue = tree[(self.size, value)]
    def createValue(self):
        return self.huffvalue

class DeflateBlock(FieldSet):
    # code: (min, max, extrabits)
    LENGTH_SYMBOLS = {257:(3,3,0),
                      258:(4,4,0),
                      259:(5,5,0),
                      260:(6,6,0),
                      261:(7,7,0),
                      262:(8,8,0),
                      263:(9,9,0),
                      264:(10,10,0),
                      265:(11,12,1),
                      266:(13,14,1),
                      267:(15,16,1),
                      268:(17,18,1),
                      269:(19,22,2),
                      270:(23,26,2),
                      271:(27,30,2),
                      272:(31,34,2),
                      273:(35,42,3),
                      274:(43,50,3),
                      275:(51,58,3),
                      276:(59,66,3),
                      277:(67,82,4),
                      278:(83,98,4),
                      279:(99,114,4),
                      280:(115,130,4),
                      281:(131,162,5),
                      282:(163,194,5),
                      283:(195,226,5),
                      284:(227,257,5),
                      285:(258,258,0)
                      }
    DISTANCE_SYMBOLS = {0:(1,1,0),
                        1:(2,2,0),
                        2:(3,3,0),
                        3:(4,4,0),
                        4:(5,6,1),
                        5:(7,8,1),
                        6:(9,12,2),
                        7:(13,16,2),
                        8:(17,24,3),
                        9:(25,32,3),
                        10:(33,48,4),
                        11:(49,64,4),
                        12:(65,96,5),
                        13:(97,128,5),
                        14:(129,192,6),
                        15:(193,256,6),
                        16:(257,384,7),
                        17:(385,512,7),
                        18:(513,768,8),
                        19:(769,1024,8),
                        20:(1025,1536,9),
                        21:(1537,2048,9),
                        22:(2049,3072,10),
                        23:(3073,4096,10),
                        24:(4097,6144,11),
                        25:(6145,8192,11),
                        26:(8193,12288,12),
                        27:(12289,16384,12),
                        28:(16385,24576,13),
                        29:(24577,32768,13),
                        }
    CODE_LENGTH_ORDER = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]
    def __init__(self, parent, name, uncomp_data="", *args, **kwargs):
        FieldSet.__init__(self, parent, name, *args, **kwargs)
        self.uncomp_data = uncomp_data
        
    def createFields(self):
        yield Bit(self, "final", "Is this the final block?") # BFINAL
        yield Enum(Bits(self, "compression_type", 2), # BTYPE
                   {0:"None", 1:"Fixed Huffman", 2:"Dynamic Huffman", 3:"Reserved"})
        if self["compression_type"].value == 0: # no compression
            padding = paddingSize(self.current_size + self.absolute_address, 8) # align on byte boundary
            if padding:
                yield PaddingBits(self, "padding[]", padding)
            yield Int16(self, "len")
            yield Int16(self, "nlen", "One's complement of len")
            if self["len"].value != ~self["nlen"].value:
                raise ParserError("len must be equal to the one's complement of nlen!")
            if self["len"].value: # null stored blocks produced by some encoders (e.g. PIL)
                yield RawBytes(self, "data", self["len"].value, "Uncompressed data")
            return
        elif self["compression_type"].value == 1: # Fixed Huffman
            length_tree = {} # (size, huffman code): value
            distance_tree = {}
            for i in xrange(144):
                length_tree[(8, i+48)] = i
            for i in xrange(144, 256):
                length_tree[(9, i+256)] = i
            for i in xrange(256, 280):
                length_tree[(7, i-256)] = i
            for i in xrange(280, 288):
                length_tree[(8, i-88)] = i
            for i in xrange(32):
                distance_tree[(5, i)] = i
        elif self["compression_type"].value == 2: # Dynamic Huffman
            yield Bits(self, "huff_num_length_codes", 5, "Number of Literal/Length Codes, minus 257")
            yield Bits(self, "huff_num_distance_codes", 5, "Number of Distance Codes, minus 1")
            yield Bits(self, "huff_num_code_length_codes", 4, "Number of Code Length Codes, minus 4")
            code_length_code_lengths = [0]*19 # confusing variable name...
            for i in self.CODE_LENGTH_ORDER[:self["huff_num_code_length_codes"].value+4]:
                field = Bits(self, "huff_code_length_code[%i]" % i, 3, "Code lengths for the code length alphabet")
                yield field
                code_length_code_lengths[i] = field.value
            code_length_tree = build_tree(code_length_code_lengths)
            length_code_lengths = []
            distance_code_lengths = []
            for numcodes, name, lengths in (
                (self["huff_num_length_codes"].value + 257, "length", length_code_lengths),
                (self["huff_num_distance_codes"].value + 1, "distance", distance_code_lengths)):
                while len(lengths) < numcodes:
                    field = HuffmanCode(self, "huff_%s_code[]" % name, code_length_tree)
                    value = field.realvalue
                    if value < 16:
                        prev_value = value
                        field._description = "Literal Code Length %i (Huffman Code %i)" % (value, field.value)
                        yield field
                        lengths.append(value)
                    else:
                        info = {16: (3,6,2),
                                17: (3,10,3),
                                18: (11,138,7)}[value]
                        if value == 16:
                            repvalue = prev_value
                        else:
                            repvalue = 0
                        field._description = "Repeat Code %i, Repeating value (%i) %i to %i times (Huffman Code %i)" % (value, repvalue, info[0], info[1], field.value)
                        yield field
                        extrafield = Bits(self, "huff_%s_code_extra[%s" % (name, field.name.split('[')[1]), info[2])
                        num_repeats = extrafield.value+info[0]
                        extrafield._description = "Repeat Extra Bits (%i), total repeats %i"%(extrafield.value, num_repeats)
                        yield extrafield
                        lengths += [repvalue]*num_repeats
            length_tree = build_tree(length_code_lengths)
            distance_tree = build_tree(distance_code_lengths)
        else:
            raise ParserError("Unsupported compression type 3!")
        while True:
            field = HuffmanCode(self, "length_code[]", length_tree)
            value = field.realvalue
            if value < 256:
                field._description = "Literal Code %r (Huffman Code %i)" % (chr(value), field.value)
                yield field
                self.uncomp_data += chr(value)
            if value == 256:
                field._description = "Block Terminator Code (256) (Huffman Code %i)" % field.value
                yield field
                break
            elif value > 256:
                info = self.LENGTH_SYMBOLS[value]
                if info[2] == 0:
                    field._description = "Length Code %i, Value %i (Huffman Code %i)" % (value, info[0], field.value)
                    length = info[0]
                    yield field
                else:
                    field._description = "Length Code %i, Values %i to %i (Huffman Code %i)" % (value, info[0], info[1], field.value)
                    yield field
                    extrafield = Bits(self, "length_extra[%s" % field.name.split('[')[1], info[2])
                    length = extrafield.value + info[0]
                    extrafield._description = "Length Extra Bits (%i), total length %i"%(extrafield.value, length)
                    yield extrafield
                field = HuffmanCode(self, "distance_code[]", distance_tree)
                value = field.realvalue
                info = self.DISTANCE_SYMBOLS[value]
                if info[2] == 0:
                    field._description = "Distance Code %i, Value %i (Huffman Code %i)" % (value, info[0], field.value)
                    distance = info[0]
                    yield field
                else:
                    field._description = "Distance Code %i, Values %i to %i (Huffman Code %i)" % (value, info[0], info[1], field.value)
                    yield field
                    extrafield = Bits(self, "distance_extra[%s" % field.name.split('[')[1], info[2])
                    distance = extrafield.value + info[0]
                    extrafield._description = "Distance Extra Bits (%i), total length %i"%(extrafield.value, distance)
                    yield extrafield
                self.uncomp_data = extend_data(self.uncomp_data, length, distance)

class DeflateData(GenericFieldSet):
    endian = LITTLE_ENDIAN
    def createFields(self):
        uncomp_data = ""
        blk=DeflateBlock(self, "compressed_block[]", uncomp_data)
        yield blk
        uncomp_data = blk.uncomp_data
        while not blk["final"].value:
            blk=DeflateBlock(self, "compressed_block[]", uncomp_data)
            yield blk
            uncomp_data = blk.uncomp_data
        padding = paddingSize(self.current_size + self.absolute_address, 8) # align on byte boundary
        if padding:
            yield PaddingBits(self, "padding[]", padding)
        self.uncompressed_data = uncomp_data

class ZlibData(Parser):
    PARSER_TAGS = {
        "id": "zlib",
        "category": "archive",
        "file_ext": ("zlib",),
        "min_size": 8*8,
        "description": "ZLIB Data",
    }
    endian = LITTLE_ENDIAN

    def validate(self):
        if self["compression_method"].value != 8:
            return "Incorrect compression method"
        if ((self["compression_info"].value << 12) +
            (self["compression_method"].value << 8) +
            (self["flag_compression_level"].value << 6) +
            (self["flag_dictionary_present"].value << 5) +
            (self["flag_check_bits"].value)) % 31 != 0:
            return "Invalid flag check value"
        return True

    def createFields(self):
        yield Enum(Bits(self, "compression_method", 4), {8:"deflate", 15:"reserved"}) # CM
        yield Bits(self, "compression_info", 4, "base-2 log of the window size") # CINFO
        yield Bits(self, "flag_check_bits", 5) # FCHECK
        yield Bit(self, "flag_dictionary_present") # FDICT
        yield Enum(Bits(self, "flag_compression_level", 2), # FLEVEL
                   {0:"Fastest", 1:"Fast", 2:"Default", 3:"Maximum, Slowest"})
        if self["flag_dictionary_present"].value:
            yield textHandler(UInt32(self, "dict_checksum", "ADLER32 checksum of dictionary information"), hexadecimal)
        yield DeflateData(self, "data", self.stream, description = "Compressed Data")
        yield textHandler(UInt32(self, "data_checksum", "ADLER32 checksum of compressed data"), hexadecimal)

def zlib_inflate(stream, wbits=None, prevdata=""):
    if wbits is None or wbits >= 0:
        return ZlibData(stream)["data"].uncompressed_data
    else:
        data = DeflateData(None, "root", stream, "", stream.askSize(None))
        for unused in data:
            pass
        return data.uncompressed_data
