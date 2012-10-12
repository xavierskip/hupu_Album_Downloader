#!/usr/bin/env python
#coding: utf-8
import os,sys,urllib2,re

home = r'http://my.hupu.com/McGrady1jia/photo/a154963-2.html'
homepage = urllib2.urlopen(home).read()
path = re.match(r'http://my\.hupu\.com([\S]+-)[\d]*\.html',home).group(1)
print path
pat  = path+ r'([\d]+).html(?:\'|\")>'
print pat
P_num = re.findall(pat,homepage)
print P_num
num = int(P_num[-1])
print num
page_list = ['http://my.hupu.com%s%d.html' %(path,i) for i in xrange(1,num+1)]
print page_list