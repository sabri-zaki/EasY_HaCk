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


class colors:

	def red(self,num):
		return "\033["+str(num)+";31m"

	def green(self,num):
		return "\033["+str(num)+";32m"

	def yellow(self,num):
		return "\033["+str(num)+";33m"

	def white(self,num):
		return "\033["+str(num)+";38m"

	def reset(self):
		return "\033[0m"

	def blue(self,num):
		return "\033["+str(num)+";34m"
