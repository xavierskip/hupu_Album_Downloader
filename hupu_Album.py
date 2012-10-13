#!/usr/bin/env python
#coding: utf-8
#author: xavierskip
#date:10-13-2012
'''
issues:
	抓取时没有的封面图没有去除，总共有几页图就会多几张图
todo:
	去除重复的图片 
'''
import os,sys,urllib2,re

def get_pages(home,homepage):
	path = re.match(r'http://my\.hupu\.com([\S]+-)[\d]*\.html',home).group(1)
	pat  = path+ r'([\d]+).html(?:\'|\")>' #最大页面值
	P_nums = re.findall(pat,homepage)
	P_max = int(P_nums[-1])
	page_list = [r'http://my.hupu.com%s%d.html' %(path,i) for i in xrange(1,P_max+1)]
	print page_list #output
	return page_list

def get_content(url):
	content = urllib2.urlopen(url).read()
	print 'page done! %s' %url
	return content

def url_list(content):
	pat = 'http://i[\d]{1}\.hoopchina\.com\.cn/.+small\.(?:jpg|gif|png|jpeg)'
	url_list = re.findall(pat,content)
	return url_list

def tourls(url_list):
	url = '\n'.join(url_list)
	url = re.sub('small\.','big.',url)
	return url

def dowm_img(urls):
	pass

def main():
	#脚本可带url参数
	if len(sys.argv)<=1:
		home = r'http://my.hupu.com/jzgk/photo/a74456-1.html' #脚本内置虎扑相册地址
	else:
		home = sys.argv[1]
	homepage = urllib2.urlopen(home).read()
	title    = re.search(r'<title>(.+)</title>',homepage).group(1)
	print '正在抓取-%s-相册' %title.decode('gb2312').encode('utf-8')
	page_list = get_pages(home,homepage)
	content = ''
	for i in page_list:
		content +=get_content(i)
	#print content
	U_list = url_list(content)
	urls = tourls(U_list)
	print urls
	url_file = open('urls','w') #追加 w+
	try:
		url_file.write(urls)
	finally:
		url_file.close()
	#os.system('wget %s' %urls)

if __name__ == '__main__':
    main()
