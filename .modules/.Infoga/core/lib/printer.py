#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Infoga: Email Information Gathering
#
# @url: https://github.com/m4ll0k/Infoga
# @author: Momo Outaadi (M4ll0k)
#
# Infoga is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3 of the License.
#
# Infoga is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Infoga; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import colors

class printer:
	#
	red = colors.colors().red(1)
	white = colors.colors().white(0)
	green = colors.colors().green(1)
	blue = colors.colors().blue(1)
	end = colors.colors().reset()
	#
	def plus(self,string,flag="+"):
		print "%s[%s]%s %s%s%s"%(self.green,flag,self.end,self.white,string,self.end)

	def test(self,string,flag="*"):
		print "%s[%s]%s %s%s%s"%(self.blue,flag,self.end,self.blue,string,self.end)

	def error(self,string,flag="!"):
		print "%s[%s]%s %s%s%s"%(self.red,flag,self.end,self.red,string,self.end)

	def ip(self,string,flag="|"):
		print " %s%s%s  %s%s%s\n"%(self.green,flag,self.end,self.white,string,self.end)

	def info(self,string,color="g",flag="|"):
		if color == "g":
			print "\t  %s%s%s  %s%s%s"%(self.green,flag,self.end,self.white,string,self.end)
		if color == "r":
			print "\t  %s%s%s  %s%s%s"%(self.red,flag,self.end,self.red,string,self.end)