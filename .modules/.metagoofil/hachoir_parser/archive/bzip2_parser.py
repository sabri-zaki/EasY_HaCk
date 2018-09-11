"""
BZIP2 archive file

Author: Victor Stinner, Robert Xiao
"""

from hachoir_parser import Parser
from hachoir_core.tools import paddingSize
from hachoir_core.field import (Field, FieldSet, GenericVector,
    ParserError, String,
    PaddingBits, Bit, Bits, Character,
    UInt32, Enum, CompressedField)
from hachoir_core.endian import BIG_ENDIAN
from hachoir_core.text_handler import textHandler, hexadecimal
from hachoir_parser.archive.zlib import build_tree, HuffmanCode

try:
    from bz2 import BZ2Decompressor

    class Bunzip2:
        def __init__(self, stream):
            self.bzip2 = BZ2Decompressor()

        def __call__(self, size, data=''):
            try:
                return self.bzip2.decompress(data)
            except EOFError:
                return ''

    has_deflate = True
except ImportError:
    has_deflate = False

class ZeroTerminatedNumber(Field):
    """Zero (bit) terminated number: e.g. 11110 is 4."""
    def __init__(self, parent, name, description=None):
        Field.__init__(self, parent, name, 0, description)

        endian = self.parent.endian
        stream = self.parent.stream
        addr = self.absolute_address

        value = 0
        while True:
            bit = stream.readBits(addr, 1, endian)
            addr += 1
            self._size += 1
            if not bit:
                break
            value += 1
        self._value = value
    def createValue(self):
        return self._value

def move_to_front(l, c):
    l[:] = l[c:c+1] + l[0:c] + l[c+1:]

class Bzip2Bitmap(FieldSet):
    def __init__(self, parent, name, nb_items, start_index, *args, **kwargs):
        FieldSet.__init__(self, parent, name, *args, **kwargs)
        self.nb_items = nb_items
        self.start_index = start_index

    def createFields(self):
        for i in xrange(self.start_index, self.start_index+self.nb_items):
            yield Bit(self, "symbol_used[%i]"%i, "Is the symbol %i (%r) used?"%(i, chr(i)))

class Bzip2Lengths(FieldSet):
    def __init__(self, parent, name, symbols, *args, **kwargs):
        FieldSet.__init__(self, parent, name, *args, **kwargs)
        self.symbols = symbols

    def createFields(self):
        yield Bits(self, "start_length", 5)
        length = self["start_length"].value
        lengths = []
        for i in xrange(self.symbols):
            while True:
                bit = Bit(self, "change_length[%i][]"%i, "Should the length be changed for symbol %i?"%i)
                yield bit
                if not bit.value:
                    break
                else:
                    bit = Enum(Bit(self, "length_decrement[%i][]"%i, "Decrement the value?"), {True: "Decrement", False: "Increment"})
                    yield bit
                    if bit.value:
                        length -= 1
                    else:
                        length += 1
            lengths.append(length)
        self.final_length = length
        self.tree = build_tree(lengths)

class Bzip2Selectors(FieldSet):
    def __init__(self, parent, name, ngroups, *args, **kwargs):
        FieldSet.__init__(self, parent, name, *args, **kwargs)
        self.groups = range(ngroups)

    def createFields(self):
        for i in xrange(self["../selectors_used"].value):
            field = ZeroTerminatedNumber(self, "selector_list[]")
            move_to_front(self.groups, field.value)
            field.realvalue = self.groups[0]
            field._description = "MTF'ed selector index: raw value %i, real value %i"%(field.value, field.realvalue)
            yield field

class Bzip2Block(FieldSet):
    def createFields(self):
        yield textHandler(Bits(self, "blockheader", 48, "Block header"), hexadecimal)
        if self["blockheader"].value != 0x314159265359: # pi
            raise ParserError("Invalid block header!")
        yield textHandler(UInt32(self, "crc32", "CRC32 for this block"), hexadecimal)
        yield Bit(self, "randomized", "Is this block randomized?")
        yield Bits(self, "orig_bwt_pointer", 24, "Starting pointer into BWT after untransform")
        yield GenericVector(self, "huffman_used_map", 16, Bit, 'block_used', "Bitmap showing which blocks (representing 16 literals each) are in use")
        symbols_used = []
        for index, block_used in enumerate(self["huffman_used_map"].array('block_used')):
            if block_used.value:
                start_index = index*16
                field = Bzip2Bitmap(self, "huffman_used_bitmap[%i]"%index, 16, start_index, "Bitmap for block %i (literals %i to %i) showing which symbols are in use"%(index, start_index, start_index + 15))
                yield field
                for i, used in enumerate(field):
                    if used.value:
                        symbols_used.append(start_index + i)
        yield Bits(self, "huffman_groups", 3, "Number of different Huffman tables in use")
        yield Bits(self, "selectors_used", 15, "Number of times the Huffman tables are switched")
        yield Bzip2Selectors(self, "selectors_list", self["huffman_groups"].value)
        trees = []
        for group in xrange(self["huffman_groups"].value):
            field = Bzip2Lengths(self, "huffman_lengths[]", len(symbols_used)+2)
            yield field
            trees.append(field.tree)
        counter = 0
        rle_run = 0
        selector_tree = None
        while True:
            if counter%50 == 0:
                select_id = self["selectors_list"].array("selector_list")[counter//50].realvalue
                selector_tree = trees[select_id]
            field = HuffmanCode(self, "huffman_code[]", selector_tree)
            if field.realvalue in [0, 1]:
                # RLE codes
                if rle_run == 0:
                    rle_power = 1
                rle_run += (field.realvalue + 1) * rle_power
                rle_power <<= 1
                field._description = "RLE Run Code %i (for %r); Total accumulated run %i (Huffman Code %i)" % (field.realvalue, chr(symbols_used[0]), rle_run, field.value)
            elif field.realvalue == len(symbols_used)+1:
                field._description = "Block Terminator (%i) (Huffman Code %i)"%(field.realvalue, field.value)
                yield field
                break
            else:
                rle_run = 0
                move_to_front(symbols_used, field.realvalue-1)
                field._description = "Literal %r (value %i) (Huffman Code %i)"%(chr(symbols_used[0]), field.realvalue, field.value)
            yield field
            if field.realvalue == len(symbols_used)+1:
                break
            counter += 1

class Bzip2Stream(FieldSet):
    START_BLOCK = 0x314159265359 # pi
    END_STREAM = 0x177245385090 # sqrt(pi)
    def createFields(self):
        end = False
        while not end:
            marker = self.stream.readBits(self.absolute_address + self.current_size, 48, self.endian)
            if marker == self.START_BLOCK:
                yield Bzip2Block(self, "block[]")
            elif marker == self.END_STREAM:
                yield textHandler(Bits(self, "stream_end", 48, "End-of-stream marker"), hexadecimal)
                yield textHandler(UInt32(self, "crc32", "CRC32 for entire stream"), hexadecimal)
                padding = paddingSize(self.current_size, 8)
                if padding:
                    yield PaddingBits(self, "padding[]", padding)
                end = True
            else:
                raise ParserError("Invalid marker 0x%02X!"%marker)

class Bzip2Parser(Parser):
    PARSER_TAGS = {
        "id": "bzip2",
        "category": "archive",
        "file_ext": ("bz2",),
        "mime": (u"application/x-bzip2",),
        "min_size": 10*8,
        "magic": (('BZh', 0),),
        "description": "bzip2 archive"
    }
    endian = BIG_ENDIAN

    def validate(self):
        if self.stream.readBytes(0, 3) != 'BZh':
            return "Wrong file signature"
        if not("1" <= self["blocksize"].value <= "9"):
            return "Wrong blocksize"
        return True

    def createFields(self):
        yield String(self, "id", 3, "Identifier (BZh)", charset="ASCII")
        yield Character(self, "blocksize", "Block size (KB of memory needed to uncompress)")

        if self._size is None: # TODO: is it possible to handle piped input?
            raise NotImplementedError

        size = (self._size - self.current_size)/8
        if size:
            for tag, filename in self.stream.tags:
                if tag == "filename" and filename.endswith(".bz2"):
                    filename = filename[:-4]
                    break
            else:
                filename = None
            data = Bzip2Stream(self, "file", size=size*8)
            if has_deflate:
                CompressedField(self, Bunzip2)
                def createInputStream(**args):
                    if filename:
                        args.setdefault("tags",[]).append(("filename", filename))
                    return self._createInputStream(**args)
                data._createInputStream = createInputStream
            yield data

