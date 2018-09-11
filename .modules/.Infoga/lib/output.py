#!/usr/bin/env python3
# -*- coding:utf-8 -*- 
#
# @name   : Infoga - Email Information Gathering
# @url    : http://github.com/m4ll0k
# @author : Momo Outaadi (m4ll0k)

from lib.colors import *

def plus(string):print("%s[+]%s %s"%(G%0,E,string))
def warn(string):print("%s[!]%s %s"%(R%0,E,string))
def test(string):print("%s[*]%s %s"%(B%0,E,string))
def info(string):print("%s[i]%s %s"%(Y%0,E,string))
def more(string):print(" %s|%s  %s"%(W%0,E,string))
# pwned data
def ppwned(data,ver):
	if 'found' in data['status']:
		warn('This email was leaked... found %s results..'%(data['results']))
		if ver == 2 or ver == 3:
			for i in range(0,len(data['data'])):
				more('Leaked in: %s'%data['data'][i]['title'])
				more('Data Leaked: %s'%data['data'][i]['date_leaked'])
				more('Details: %s'%data['data'][i]['details'])
				more('Source Network: %s'%data['data'][i]['source_network'])
				print("")
# print shodan return data
def data(ip,data,email,ver):
	if   ver == 1:plus('Email: %s (%s)'%(email,ip))
	elif ver == 2:
		try:
			plus('Email: %s (%s)'%(email,ip))
			if data['hostnames']:more('Hostname: %s'%(data['hostnames'][0]))
			if data['country_code'] and data['country_name']:more('Country: %s (%s)'%(data['country_code'],data['country_name']))
			if data['city'] and data['region_code']:more('City: %s (%s)'%(data['city'],data['region_code']))
		except KeyError as e:
			pass
	elif ver == 3:
		try:
			plus('Email: %s (%s)'%(email,ip))
			if data['hostnames']:more('Hostname: %s'%(data['hostnames'][0]))
			if data['country_code'] and data['country_name']:more('Country: %s (%s)'%(data['country_code'],data['country_name']))
			if data['city'] and data['region_code']:more('City: %s (%s)'%(data['city'],data['region_code']))
			if data['asn']:more('ASN: %s'%(data['asn']))
			if data['isp']:more('ISP: %s'%(data['isp']))
			if data['latitude'] and data['longitude']:more('Map: Map: https://www.google.com/maps/@%s,%s,10z (%s,%s)'%(
				data['latitude'],data['longitude'],data['latitude'],data['longitude']))
			if data['org']:more('Organization: %s'%(data['org']))
			if data['ports']:more('Ports: %s'%(data['ports']))
			if data['vulns']:more('Vulns: %s'%(data['vulns']))
		except KeyError as e:
			pass
	print("")