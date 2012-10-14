#!/usr/bin/env python
#coding: utf-8
import os,sys,urllib2,re

path  = 'test 路径'
os.system('mkdir "%s"' %path)
print '创建路径成功%s' %path
'''
# 抓取 标题
home = r'http://my.hupu.com/jzgk/photo/a75782-1.html'
homepage = urllib2.urlopen(home).read()
title    = re.search(r'<title>(.+)</title>',homepage)
print title.group(1)
t = title.group(1)
print '正在下载『%s』相册' %t
os.system(r'mkdir "%s"' %t)
f = open(r'%s/urls' %t,'w')
f.write('hello urls \n 搞定！')
f.close()
print 'done'
'''

'''
# 带参数
if len(sys.argv)<=1:
	home = r'default'
else:
	home = sys.argv[1]
print home

#相册有几页？
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
'''