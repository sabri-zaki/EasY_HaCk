## Hash
# -*- coding: utf-8 -*-
##
'''
Hash Cracker v1.0
Developer: SABRI ZAKI
Date: 07/07/2018
Team: Alpha Team DZ
Facebook : www.facebook.com/sabri.zaki.31
'''
import os
import sys
import time
import hashlib
from core.misc import *
from core.dcrypt import *
from core.ecrypt import *

# Console colors
N  = '\033[0m'    # normal
R  = '\033[1;31m' # red
Y  = '\033[1;33m' # yellow
W  = '\033[1;37m' # white

def restart_Hash():
	python = sys.executable
	os.execl(python, python, * sys.argv)
	curdir = os.getcwd()

try:
	clearscreen()
	leethash_banner()
	print (R + "[" + Y + "#" + R + "]" + W + " Developer" + R + ": " + W + "SABRI ZAKI" + N)
	print (R + "[" + Y + "#" + R + "]" + W + " Date  " + R + ": " + W + "07/07/2018" + N)
	print (R + "[" + Y + "#" + R + "]" + W + " Team  " + R + ": " + W + "Alpha Teame DZ" + N)
	print (R + "[" + Y + "#" + R + "]" + W + " Facebook" + R + ": " + W + "www.facebook.com/sabri.zaki.31" + N)
	encryptordecrypt = raw_input("\n" + R + "[" + Y + "*"  + R + "] (" + Y + "G" + R + ")" + W + "enerate or " + R + "(" + Y + "C" + R + ")" + W + "rack " + Y + "Hash" + R + ":" + Y + " ")

	if encryptordecrypt == 'g' or encryptordecrypt == 'G':
		algorithm1 = raw_input('\n' + R + '[' + Y + '*' + R + ']' + W + ' Algorithm ' + R + '[' + Y + ' md5' + R + '|' + Y + 'sha1' + R + '|' + Y + 'sha224' + R + '|' + Y + 'sha256' + R + '|' + Y + 'sha384' + R + '|' + Y + 'sha512 ' + R + ']:' + Y + ' ')
		if algorithm1 == "md5" or algorithm1 == "MD5" or algorithm1 == "Md5" or algorithm1 == "mD5":
			md5hash()
		elif algorithm1 == "sha1" or algorithm1 == "SHA1" or algorithm1 == "Sha1" or algorithm1 == "sHa1" or algorithm1 == "sHA1":
			sha1hash()
		elif algorithm1 == "sha224" or algorithm1 == "SHA224" or algorithm1 == "Sha224" or algorithm1 == "sHa224" or algorithm1 == "sHA224":
			sha224hash()
		elif algorithm1 == "sha256" or algorithm1 == "SHA256" or algorithm1 == "Sha256" or algorithm1 == "sHa256" or algorithm1 == "sHA256":
			sha256hash()
		elif algorithm1 == "sha384" or algorithm1 == "SHA384" or algorithm1 == "Sha384" or algorithm1 == "sHa384" or algorithm1 == "sHA384":
			sha384hash()
		elif algorithm1 == "sha512" or algorithm1 == "SHA512" or algorithm1 == "Sha512" or algorithm1 == "sHa512" or algorithm1 == "sHA512":
			sha512hash()
		else:
			print(R + "\n[" + Y + "!" + R + "]" + R + " ERROR:" + W + " Wrong Input..." + N)
			time.sleep(2)
			restart_1337Hash()
	elif encryptordecrypt == 'c' or encryptordecrypt == 'C':
		algorithm2 = raw_input('\n' + R + '[' + Y + '*' + R + ']' + W + ' Algorithm ' + R + '[' + Y + ' md5' + R + '|' + Y + 'sha1' + R + '|' + Y + 'sha224' + R + '|' + Y + 'sha256' + R + '|' + Y + 'sha384' + R + '|' + Y + 'sha512 ' + R + ']:' + Y + ' ')
		if algorithm2 == "md5" or algorithm2 == "MD5" or algorithm2 == "Md5" or algorithm2 == "mD5":
			md5hashcrack()
		elif algorithm2 == "sha1" or algorithm2 == "SHA1" or algorithm2 == "Sha1" or algorithm2 == "sHa1" or algorithm2 == "sHA1":
			sha1hashcrack()
		elif algorithm2 == "sha224" or algorithm2 == "SHA224" or algorithm2 == "Sha224" or algorithm2 == "sHa224" or algorithm2 == "sHA224":
			sha224hashcrack()
		elif algorithm2 == "sha256" or algorithm2 == "SHA256" or algorithm2 == "Sha256" or algorithm2 == "sHa256" or algorithm2 == "sHA256":
			sha256hashcrack()
		elif algorithm2 == "sha384" or algorithm2 == "SHA384" or algorithm2 == "Sha384" or algorithm2 == "sHa384" or algorithm2 == "sHA384":
			sha384hashcrack()
		elif algorithm2 == "sha512" or algorithm2 == "SHA512" or algorithm2 == "Sha512" or algorithm2 == "sHa512" or algorithm2 == "sHA512":
			sha512hashcrack()
		else:
			print(R + "\n[" + Y + "!" + R + "]" + R + " ERROR:" + W + " Wrong Input..." + N)
			time.sleep(2)
			restart_Hash()
	else:
		print(R + "\n[" + Y + "!" + R + "]" + R + " ERROR:" + W + " Wrong Input..." + N)
		time.sleep(2)
		restart_Hash()
except(KeyboardInterrupt):
	print("\n" + R + "[" + Y + "!" + R + "]" + W + " Exiting the program..." + N)
	time.sleep(1.5)
	print(R + "[" + Y + "!" + R + "]" + W + " Have a Nice Day...\n" + N)
	time.sleep(0.5)
	sys.exit()