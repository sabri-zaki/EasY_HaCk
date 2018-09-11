## misc.py - Useful module of Hash
# -*- coding: utf-8 -*-
##
import os
import sys

__banner__ = """
\033[1;31m  _____            _   \033[0m
\033[1;31m |  |  | ___  ___ | |_ \033[0m
\033[1;31m |     || .'||_ -||   |\033[0m
\033[1;31m |__|__||__,||___||_|_| Cracker V1.0\033[0m
"""

def leethash_banner():
	print __banner__

def clearscreen():
	if sys.platform == "linux2":
		os.system("clear")
	elif sys.platform == "win32":
		os.system("cls")
	else:
		os.system("clear")