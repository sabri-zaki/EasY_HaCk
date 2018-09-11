## dcrypt.py - Useful module of 1337Hash
# -*- coding: utf-8 -*-
##
import sys
import hashlib

# Console colors
N  = '\033[0m'    # normal
R  = '\033[1;31m' # red
Y  = '\033[1;33m' # yellow
W  = '\033[1;37m' # white

def md5hashcrack():
	hash01 = raw_input(R + '[' + Y + '*' + R + ']' + W + ' Hash    ' + R + ':' + Y + ' ')
	wordlist = raw_input(R + '[' + Y + '*' + R + ']' + W + ' Type zaki.txt' + R + ':' + Y + ' ')
	try:
		words = open(wordlist, 'r')
	except IOError, e:
		print("\n%s[%s!%s] ERROR: %s%s\n%s" % (R,Y,R,W,e,N))
		sys.exit()
	
	words = words.readlines()
	for word in words:
		hash = hashlib.md5(word[:-1])
		value = hash.hexdigest()
		if hash01 == value:
			print(R + '\n[' + Y + '+' + R + ']' + W + ' Word' + R + ':' + W + ' ' + word + '\n' + N)
			sys.exit()

def sha1hashcrack():
	hash01 = raw_input(R + '[' + Y + '*' + R + ']' + W + ' Hash    ' + R + ':' + Y + ' ')
	wordlist = raw_input(R + '[' + Y + '*' + R + ']' + W + ' Wordlist' + R + ':' + Y + ' ')
	try:
		words = open(wordlist, 'r')
	except IOError, e:
		print("\n%s[%s!%s] ERROR: %s%s\n%s" % (R,Y,R,W,e,N))
		sys.exit()
	
	words = words.readlines()
	for word in words:
		hash = hashlib.sha1(word[:-1])
		value = hash.hexdigest()
		if hash01 == value:
			print(R + '\n[' + Y + '+' + R + ']' + W + ' Word' + R + ':' + W + ' ' + word + '\n' + N)
			sys.exit()

def sha224hashcrack():
	hash01 = raw_input(R + '[' + Y + '*' + R + ']' + W + ' Hash    ' + R + ':' + Y + ' ')
	wordlist = raw_input(R + '[' + Y + '*' + R + ']' + W + ' Wordlist' + R + ':' + Y + ' ')
	try:
		words = open(wordlist, 'r')
	except IOError, e:
		print("\n%s[%s!%s] ERROR: %s%s\n%s" % (R,Y,R,W,e,N))
		sys.exit()
	
	words = words.readlines()
	for word in words:
		hash = hashlib.sha224(word[:-1])
		value = hash.hexdigest()
		if hash01 == value:
			print(R + '\n[' + Y + '+' + R + ']' + W + ' Word' + R + ':' + W + ' ' + word + '\n' + N)
			sys.exit()

def sha256hashcrack():
	hash01 = raw_input(R + '[' + Y + '*' + R + ']' + W + ' Hash    ' + R + ':' + Y + ' ')
	wordlist = raw_input(R + '[' + Y + '*' + R + ']' + W + ' Wordlist' + R + ':' + Y + ' ')
	try:
		words = open(wordlist, 'r')
	except IOError, e:
		print("\n%s[%s!%s] ERROR: %s%s\n%s" % (R,Y,R,W,e,N))
		sys.exit()
	
	words = words.readlines()
	for word in words:
		hash = hashlib.sha256(word[:-1])
		value = hash.hexdigest()
		if hash01 == value:
			print(R + '\n[' + Y + '+' + R + ']' + W + ' Word' + R + ':' + W + ' ' + word + '\n' + N)
			sys.exit()

def sha384hashcrack():
	hash01 = raw_input(R + '[' + Y + '*' + R + ']' + W + ' Hash    ' + R + ':' + Y + ' ')
	wordlist = raw_input(R + '[' + Y + '*' + R + ']' + W + ' Wordlist' + R + ':' + Y + ' ')
	try:
		words = open(wordlist, 'r')
	except IOError, e:
		print("\n%s[%s!%s] ERROR: %s%s\n%s" % (R,Y,R,W,e,N))
		sys.exit()
	
	words = words.readlines()
	for word in words:
		hash = hashlib.sha384(word[:-1])
		value = hash.hexdigest()
		if hash01 == value:
			print(R + '\n[' + Y + '+' + R + ']' + W + ' Word' + R + ':' + W + ' ' + word + '\n' + N)
			sys.exit()

def sha512hashcrack():
	hash01 = raw_input(R + '[' + Y + '*' + R + ']' + W + ' Hash    ' + R + ':' + Y + ' ')
	wordlist = raw_input(R + '[' + Y + '*' + R + ']' + W + ' Wordlist' + R + ':' + Y + ' ')
	try:
		words = open(wordlist, 'r')
	except IOError, e:
		print("\n%s[%s!%s] ERROR: %s%s\n%s" % (R,Y,R,W,e,N))
		sys.exit()
	
	words = words.readlines()
	for word in words:
		hash = hashlib.sha512(word[:-1])
		value = hash.hexdigest()
		if hash01 == value:
			print(R + '\n[' + Y + '+' + R + ']' + W + ' Word' + R + ':' + W + ' ' + word + '\n' + N)
			sys.exit()