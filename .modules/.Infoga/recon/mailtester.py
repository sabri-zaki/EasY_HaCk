#!/usr/bin/env python3
# -*- coding:utf-8 -*- 
#
# @name   : Infoga - Email Information Gathering
# @url    : http://github.com/m4ll0k
# @author : Momo Outaadi (m4ll0k)

from lib.output import *
from lib.request import *
from lib.parser import *

class MailTester(Request):
	def __init__(self,email):
		Request.__init__(self)
		self.email = email

	def search(self):
		post_data = {'lang':'en'}
		post_data['email'] = self.email
		url = "http://mailtester.com/testmail.php"
		try:
			resp = self.send(
				method = 'POST',
				url = url,
				data = post_data
				)
			return self.getip(resp.content)
		except Exception as e:
			print(e)

	def getip(self,content):
		tmp_ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}',str(content),re.I)
		list_ip = []
		for ip in tmp_ip:
			if ip not in list_ip:
				list_ip.append(ip)
		return list_ip