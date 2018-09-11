"""LZX data stream parser.

Also includes a decompression function (slow!!) which can decompress
LZX data stored in a Hachoir stream.

Author: Robert Xiao
Creation date: July 18, 2007
"""
from hachoir_parser import Parser
from hachoir_core.field import (FieldSet,
    UInt32, Bit, Bits, PaddingBits,
    RawBytes, ParserError)
from hachoir_core.endian import MIDDLE_ENDIAN, LITTLE_ENDIAN
from hachoir_core.tools import paddingSize, alignValue
from hachoir_parser.archive.zlib import build_tree, HuffmanCode, extend_data
from hachoir_core.bits import str2long
import new # for instancemethod

class LZXPreTreeEncodedTree(FieldSet):
    def __init__(self, parent, name, num_elements, *args, **kwargs):
        FieldSet.__init__(self, parent, name, *args, **kwargs)
        self.num_elements = num_elements
        
    def createFields(self):
        for i in xrange(20):
            yield Bits(self, "pretree_lengths[]", 4)
        pre_tree = build_tree([self['pretree_lengths[%d]'%x].value for x in xrange(20)])
        if not hasattr(self.root, "lzx_tree_lengths_"+self.name):
            self.lengths = [0] * self.num_elements
            setattr(self.root, "lzx_tree_lengths_"+self.name, self.lengths)
        else:
            self.lengths = getattr(self.root, "lzx_tree_lengths_"+self.name)
        i = 0
        while i < self.num_elements:
            field = HuffmanCode(self, "tree_code[]", pre_tree)
            if field.realvalue <= 16:
                self.lengths[i] = (self.lengths[i] - field.realvalue) % 17
                field._description = "Literal tree delta length %i (new length value %i for element %i)" % (
                        field.realvalue, self.lengths[i], i)
                i += 1
                yield field
            elif field.realvalue == 17:
                field._description = "Tree Code 17: Zeros for 4-19 elements"
                yield field
                extra = Bits(self, "extra[]", 4)
                zeros = 4 + extra.value
                extra._description = "Extra bits: zeros for %i elements (elements %i through %i)" % (zeros, i, i+zeros-1)
                yield extra
                self.lengths[i:i+zeros] = [0] * zeros
                i += zeros
            elif field.realvalue == 18:
                field._description = "Tree Code 18: Zeros for 20-51 elements"
                yield field
                extra = Bits(self, "extra[]", 5)
                zeros = 20 + extra.value
                extra._description = "Extra bits: zeros for %i elements (elements %i through %i)" % (zeros, i, i+zeros-1)
                yield extra
                self.lengths[i:i+zeros] = [0] * zeros
                i += zeros
            elif field.realvalue == 19:
                field._description = "Tree Code 19: Same code for 4-5 elements"
                yield field
                extra = Bits(self, "extra[]", 1)
                run = 4 + extra.value
                extra._description = "Extra bits: run for %i elements (elements %i through %i)" % (run, i, i+run-1)
                yield extra
                newfield = HuffmanCode(self, "tree_code[]", pre_tree)
                assert newfield.realvalue <= 16
                newfield._description = "Literal tree delta length %i (new length value %i for elements %i through %i)" % (
                        newfield.realvalue, self.lengths[i], i, i+run-1)
                self.lengths[i:i+run] = [(self.lengths[i] - newfield.realvalue) % 17] * run
                i += run
                yield newfield

class LZXBlock(FieldSet):
    WINDOW_SIZE = {15:30,
                   16:32,
                   17:34,
                   18:36,
                   19:38,
                   20:42,
                   21:50}
    POSITION_SLOTS = {0:(0,0,0),
                      1:(1,1,0),
                      2:(2,2,0),
                      3:(3,3,0),
                      4:(4,5,1),
                      5:(6,7,1),
                      6:(8,11,2),
                      7:(12,15,2),
                      8:(16,23,3),
                      9:(24,31,3),
                      10:(32,47,4),
                      11:(48,63,4),
                      12:(64,95,5),
                      13:(96,127,5),
                      14:(128,191,6),
                      15:(192,255,6),
                      16:(256,383,7),
                      17:(384,511,7),
                      18:(512,767,8),
                      19:(768,1023,8),
                      20:(1024,1535,9),
                      21:(1536,2047,9),
                      22:(2048,3071,10),
                      23:(3072,4095,10),
                      24:(4096,6143,11),
                      25:(6144,8191,11),
                      26:(8192,12287,12),
                      27:(12288,16383,12),
                      28:(16384,24575,13),
                      29:(24576,32767,13),
                      30:(32768,49151,14),
                      31:(49152,65535,14),
                      32:(65536,98303,15),
                      33:(98304,131071,15),
                      34:(131072,196607,16),
                      35:(196608,262143,16),
                      36:(262144,393215,17),
                      37:(393216,524287,17),
                      38:(524288,655359,17),
                      39:(655360,786431,17),
                      40:(786432,917503,17),
                      41:(917504,1048575,17),
                      42:(1048576,1179647,17),
                      43:(1179648,1310719,17),
                      44:(1310720,1441791,17),
                      45:(1441792,1572863,17),
                      46:(1572864,1703935,17),
                      47:(1703936,1835007,17),
                      48:(1835008,1966079,17),
                      49:(1966080,2097151,17),
                      }
    def createFields(self):
        yield Bits(self, "block_type", 3)
        yield Bits(self, "block_size", 24)
        self.uncompressed_size = self["block_size"].value
        self.compression_level = self.root.compr_level
        self.window_size = self.WINDOW_SIZE[self.compression_level]
        self.block_type = self["block_type"].value
        curlen = len(self.parent.uncompressed_data)
        if self.block_type in (1, 2): # Verbatim or aligned offset block
            if self.block_type == 2:
                for i in xrange(8):
                    yield Bits(self, "aligned_len[]", 3)
                aligned_tree = build_tree([self['aligned_len[%d]'%i].value for i in xrange(8)])
            yield LZXPreTreeEncodedTree(self, "main_tree_start", 256)
            yield LZXPreTreeEncodedTree(self, "main_tree_rest", self.window_size * 8)
            main_tree = build_tree(self["main_tree_start"].lengths + self["main_tree_rest"].lengths)
            yield LZXPreTreeEncodedTree(self, "length_tree", 249)
            length_tree = build_tree(self["length_tree"].lengths)
            current_decoded_size = 0
            while current_decoded_size < self.uncompressed_size:
                if (curlen+current_decoded_size) % 32768 == 0 and (curlen+current_decoded_size) != 0:
                    padding = paddingSize(self.address + self.current_size, 16)
                    if padding:
                        yield PaddingBits(self, "padding[]", padding)
                field = HuffmanCode(self, "main_code[]", main_tree)
                if field.realvalue < 256:
                    field._description = "Literal value %r" % chr(field.realvalue)
                    current_decoded_size += 1
                    self.parent.uncompressed_data += chr(field.realvalue)
                    yield field
                    continue
                position_header, length_header = divmod(field.realvalue - 256, 8)
                info = self.POSITION_SLOTS[position_header]
                if info[2] == 0:
                    if info[0] == 0:
                        position = self.parent.r0
                        field._description = "Position Slot %i, Position [R0] (%i)" % (position_header, position)
                    elif info[0] == 1:
                        position = self.parent.r1
                        self.parent.r1 = self.parent.r0
                        self.parent.r0 = position
                        field._description = "Position Slot %i, Position [R1] (%i)" % (position_header, position)
                    elif info[0] == 2:
                        position = self.parent.r2
                        self.parent.r2 = self.parent.r0
                        self.parent.r0 = position
                        field._description = "Position Slot %i, Position [R2] (%i)" % (position_header, position)
                    else:
                        position = info[0] - 2
                        self.parent.r2 = self.parent.r1
                        self.parent.r1 = self.parent.r0
                        self.parent.r0 = position
                        field._description = "Position Slot %i, Position %i" % (position_header, position)
                else:
                    field._description = "Position Slot %i, Positions %i to %i" % (position_header, info[0] - 2, info[1] - 2)
                if length_header == 7:
                    field._description += ", Length Values 9 and up"
                    yield field
                    length_field = HuffmanCode(self, "length_code[]", length_tree)
                    length = length_field.realvalue + 9
                    length_field._description = "Length Code %i, total length %i" % (length_field.realvalue, length)
                    yield length_field
                else:
                    field._description += ", Length Value %i (Huffman Code %i)"%(length_header + 2, field.value)
                    yield field
                    length = length_header + 2
                if info[2]:
                    if self.block_type == 1 or info[2] < 3: # verbatim
                        extrafield = Bits(self, "position_extra[%s" % field.name.split('[')[1], info[2])
                        position = extrafield.value + info[0] - 2
                        extrafield._description = "Position Extra Bits (%i), total position %i"%(extrafield.value, position)
                        yield extrafield
                    else: # aligned offset
                        position = info[0] - 2
                        if info[2] > 3:
                            extrafield = Bits(self, "position_verbatim[%s" % field.name.split('[')[1], info[2]-3)
                            position += extrafield.value*8
                            extrafield._description = "Position Verbatim Bits (%i), added position %i"%(extrafield.value, extrafield.value*8)
                            yield extrafield
                        if info[2] >= 3:
                            extrafield = HuffmanCode(self, "position_aligned[%s" % field.name.split('[')[1], aligned_tree)
                            position += extrafield.realvalue
                            extrafield._description = "Position Aligned Bits (%i), total position %i"%(extrafield.realvalue, position)
                            yield extrafield
                    self.parent.r2 = self.parent.r1
                    self.parent.r1 = self.parent.r0
                    self.parent.r0 = position
                self.parent.uncompressed_data = extend_data(self.parent.uncompressed_data, length, position)
                current_decoded_size += length
        elif self.block_type == 3: # Uncompressed block
            padding = paddingSize(self.address + self.current_size, 16)
            if padding:
                yield PaddingBits(self, "padding[]", padding)
            else:
                yield PaddingBits(self, "padding[]", 16)
            self.endian = LITTLE_ENDIAN
            yield UInt32(self, "r[]", "New value of R0")
            yield UInt32(self, "r[]", "New value of R1")
            yield UInt32(self, "r[]", "New value of R2")
            self.parent.r0 = self["r[0]"].value
            self.parent.r1 = self["r[1]"].value
            self.parent.r2 = self["r[2]"].value
            yield RawBytes(self, "data", self.uncompressed_size)
            self.parent.uncompressed_data+=self["data"].value
            if self["block_size"].value % 2:
                yield PaddingBits(self, "padding", 8)
        else:
            raise ParserError("Unknown block type %d!"%self.block_type)

class LZXStream(Parser):
    endian = MIDDLE_ENDIAN
    def createFields(self):
        self.uncompressed_data = ""
        self.r0 = 1
        self.r1 = 1
        self.r2 = 1
        yield Bit(self, "filesize_indicator")
        if self["filesize_indicator"].value:
            yield UInt32(self, "filesize")
        while self.current_size < self.size:
            block = LZXBlock(self, "block[]")
            yield block
            if self.size - self.current_size < 16:
                padding = paddingSize(self.address + self.current_size, 16)
                if padding:
                    yield PaddingBits(self, "padding[]", padding)
                break

def lzx_decompress(stream, window_bits):
    data = LZXStream(stream)
    data.compr_level = window_bits
    for unused in data:
        pass
    return data.uncompressed_data
