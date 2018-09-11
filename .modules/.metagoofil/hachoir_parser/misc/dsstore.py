"""
Mac OS X .DS_Store parser.

Documents:
- http://search.cpan.org/~wiml/Mac-Finder-DSStore-0.95/DSStoreFormat.pod
Author: Robert Xiao
Created: 2010-09-01
"""

from hachoir_parser import HachoirParser
from hachoir_core.field import (RootSeekableFieldSet, FieldSet,
    NullBytes, RawBytes, PaddingBytes, Bytes, SubFile, String, PascalString8,
    Bits, UInt8, UInt16, UInt32,
    Link,
    ParserError)
from hachoir_core.endian import BIG_ENDIAN
from hachoir_core.text_handler import displayHandler, hexadecimal
from hachoir_core.tools import paddingSize

class BlockAddress(FieldSet):
    static_size = 32

    def createFields(self):
        yield displayHandler(Bits(self, "offset", 27, description="Offset into file divided by 32"), lambda x: hex(x*32).strip('L'))
        yield displayHandler(Bits(self, "size", 5, description="Power-of-2 size of the block"), lambda x: hex(1<<x).strip('L'))

    def createValue(self):
        return (self['offset'].value*32, 1<<self['size'].value)

    def createDisplay(self):
        if self['size'].value == 0:
            return 'null block'
        return self['offset'].display + '/' + self['size'].display

class BudHeader(FieldSet):
    static_size = 32*8

    def createFields(self):
        yield Bytes(self, "magic", 4, description="Always Bud1")
        yield UInt32(self, "allocator_offset")
        yield UInt32(self, "allocator_size")
        yield UInt32(self, "allocator_offset_backup", description="Finder will refuse to read the file if this does not match the first copy")
        for i in xrange(4):
            yield BlockAddress(self, "block_address_copy[]", description="Copies of block addresses defined in the allocator")

class BudDirectory(FieldSet):
    def createFields(self):
        yield PascalString8(self, "name", charset="MacRoman")
        yield UInt32(self, "block")

    def createValue(self):
        return (self['name'].value, self['block'].value)

    def createDisplay(self):
        return self['name'].display

class FreeList(FieldSet):
    def createFields(self):
        yield UInt32(self, "count")
        for i in xrange(self['count'].value):
            yield UInt32(self, "offset[]")

class BudAllocator(FieldSet):
    def createFields(self):
        yield UInt32(self, "nblocks")
        yield UInt32(self, "unknown", description="Always 0")
        for i in xrange(self['nblocks'].value):
            yield BlockAddress(self, "block[]")
        padding = paddingSize(self['nblocks'].value, 256)
        if padding:
            yield NullBytes(self, "padding", padding*4, description="padding to make the number of blocks a multiple of 256")
        yield UInt32(self, "ndirs")
        for i in xrange(self['ndirs'].value):
            yield BudDirectory(self, "dir[]")
        for i in xrange(32):
            yield FreeList(self, "freelist[]")
        if self.current_size < self.size:
            yield PaddingBytes(self, "slack", (self.size-self.current_size)//8, description="slack space")

class DSDB(FieldSet):
    def createFields(self):
        yield UInt32(self, "root_block", "The block number of the root node of the B-tree")
        yield UInt32(self, "tree_levels", "The number of levels of internal nodes (tree height minus one)")
        yield UInt32(self, "num_records", "The number of records in the tree")
        yield UInt32(self, "num_nodes", "The number of nodes in the tree (tree nodes, not including this header block)")
        yield UInt32(self, "unknown", "Always 0x1000, probably the tree node page size")
        if self.current_size < self.size:
            yield PaddingBytes(self, "slack", (self.size-self.current_size)//8, description="slack space")

class PascalString32UTF16(FieldSet):
    def createFields(self):
        yield UInt32(self, "size")
        yield String(self, "value", self['size'].value*2, charset="UTF-16-BE")
    def createValue(self):
        return self['value'].value
    def createDisplay(self):
        return unicode(self['value'].display)

class DSRecord(FieldSet):
    def createFields(self):
        yield PascalString32UTF16(self, "filename")
        yield Bytes(self, "property", 4)
        yield Bytes(self, "type", 4)
        type = self['type'].value
        if type == 'long':
            yield UInt32(self, "value")
        elif type == 'shor':
            yield NullBytes(self, "padding", 2)
            yield UInt16(self, "value")
        elif type == 'bool':
            yield UInt8(self, "value")
        elif type == 'blob':
            yield UInt32(self, "size")
            yield SubFile(self, "value", self['size'].value)
        elif type == 'type':
            yield Bytes(self, "value", 4)
        elif type == 'ustr':
            yield PascalString32UTF16(self, "value")
        else:
            raise ParserError("Unknown record type %s"%type)

    def createValue(self):
        return (self['filename'].value, self['property'].value, self['value'].value)

    def createDisplay(self):
        return self['filename'].display + ':' + self['property'].value

class BTNode(FieldSet):
    def linkValue(self, block):
        return (lambda: self['/node[%d]'%block.value])

    def createFields(self):
        yield UInt32(self, "last_block")
        yield UInt32(self, "count")
        if self['last_block'].value != 0:
            for i in xrange(self['count'].value):
                block = UInt32(self, "child_block[]")
                yield block
                link = Link(self, "child_link[]")
                link.createValue = self.linkValue(block)
                yield link
                yield DSRecord(self, "record[]")
            link = Link(self, "child_link[]")
            link.createValue = self.linkValue(self['last_block'])
            yield link
        else:
            for i in xrange(self['count'].value):
                yield DSRecord(self, "record[]")
        if self.current_size < self.size:
            yield PaddingBytes(self, "slack", (self.size-self.current_size)//8, description="slack space")

class DSStore(HachoirParser, RootSeekableFieldSet):
    endian = BIG_ENDIAN
    MAGIC = '\0\0\0\1Bud1'
    PARSER_TAGS = {
        "id": "dsstore",
        "category": "misc",
        "file_ext": ("DS_Store",),
        "magic": ((MAGIC, 0),),
        "min_size": 4+32, # \0\0\0\1 + 32-byte header
        "description": "Mac OS X DS_Store",
    }

    def __init__(self, stream, **args):
        RootSeekableFieldSet.__init__(self, None, "root", stream, None, stream.askSize(self))
        HachoirParser.__init__(self, stream, **args)

    def validate(self):
        if self.stream.readBytes(0, len(self.MAGIC)) != self.MAGIC:
            return "Invalid magic"
        return True

    def getBlock(self, block_number):
        return self['allocator'].array('block')[block_number].value

    def createFields(self):
        yield UInt32(self, "unknown", description="Always 1")
        yield BudHeader(self, "header")
        self.seekByte(self['header/allocator_offset'].value+4)
        yield BudAllocator(self, "allocator", size=self['header/allocator_size'].value*8)
        for dir in self['allocator'].array('dir'):
            if dir['name'].value == 'DSDB':
                break
        else:
            raise ParserError("DSDB not found.")
        offs, size = self.getBlock(dir['block'].value)
        self.seekByte(offs+4)
        yield DSDB(self, "dsdb", size=size*8)

        blocks = [self['dsdb/root_block'].value]
        while blocks:
            block = blocks.pop()
            offs, size = self.getBlock(block)
            self.seekByte(offs+4)
            node = BTNode(self, "node[%d]"%block, size=size*8)
            yield node
            if node['last_block'].value != 0:
                new_blocks = []
                for block in node.array('child_block'):
                    new_blocks.append(block.value)
                new_blocks.append(node['last_block'].value)
                blocks.extend(reversed(new_blocks)) # dfs
                #blocks = new_blocks[::-1] + blocks # bfs

        for i, fl in enumerate(self['allocator'].array('freelist')):
            if fl['count'].value == 0: continue
            for offs in fl.array('offset'):
                size = min(1<<i, self.size//8-offs.value-4)
                if size > 0:
                    self.seekByte(offs.value+4)
                    yield RawBytes(self, "free[]", size)
