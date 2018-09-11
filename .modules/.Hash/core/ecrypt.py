## ecrypt.py - Useful module of 1337Hash
# -*- coding: utf-8 -*-
##
import sys
import hashlib

# Console colors
N  = '\033[0m'    # normal
R  = '\033[1;31m' # red
Y  = '\033[1;33m' # yellow
W  = '\033[1;37m' # white

def md5hash():
	hash = hashlib.md5(raw_input(R + '[' + Y + '*' + R + ']' + W + ' String' + R + ':' + Y + ' ')).hexdigest()
	print(R + '[' + Y + '+' + R + ']' + W + ' Hash  ' + R + ':' + Y + ' ' + hash + N)
	sys.exit()

def sha1hash():
	hash = hashlib.sha1(raw_input(R + '[' + Y + '*' + R + ']' + W + ' String' + R + ':' + Y + ' ')).hexdigest()
	print(R + '[' + Y + '+' + R + ']' + W + ' Hash  ' + R + ':' + Y + ' ' + hash + N)
	sys.exit()

def sha224hash():
	hash = hashlib.sha224(raw_input(R + '[' + Y + '*' + R + ']' + W + ' String' + R + ':' + Y + ' ')).hexdigest()
	print(R + '[' + Y + '+' + R + ']' + W + ' Hash  ' + R + ':' + Y + ' ' + hash + N)
	sys.exit()

def sha256hash():
	hash = hashlib.sha256(raw_input(R + '[' + Y + '*' + R + ']' + W + ' String' + R + ':' + Y + ' ')).hexdigest()
	print(R + '[' + Y + '+' + R + ']' + W + ' Hash  ' + R + ':' + Y + ' ' + hash + N)
	sys.exit()

def sha384hash():
	hash = hashlib.sha384(raw_input(R + '[' + Y + '*' + R + ']' + W + ' String' + R + ':' + Y + ' ')).hexdigest()
	print(R + '[' + Y + '+' + R + ']' + W + ' Hash  ' + R + ':' + Y + ' ' + hash + N)
	sys.exit()

def sha512hash():
	hash = hashlib.sha512(raw_input(R + '[' + Y + '*' + R + ']' + W + ' String' + R + ':' + Y + ' ')).hexdigest()
	print(R + '[' + Y + '+' + R + ']' + W + ' Hash  ' + R + ':' + Y + ' ' + hash + N)
	sys.exit()