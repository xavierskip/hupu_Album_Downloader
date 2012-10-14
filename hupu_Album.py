#!/usr/bin/env python
#coding: utf-8
#author: xavierskip
#date:10-13-2012
'''
issues:
	抓取时没有的封面图没有去除，总共有几页图就会多几张图
	正则只匹配出jpg|gif|png|jpeg格式的图片url，还有其他的么？
todo:
	去除重复的图片url
'''
import os,sys,urllib2,re

def get_pages(home,homepage):
	path = re.match(r'http://my\.hupu\.com([\S]+-)[\d]*\.html',home).group(1)    #Album path
	pat  = path+ r'([\d]+).html(?:\'|\")>' 
	P_nums = re.findall(pat,homepage)
	P_max = int(P_nums[-1])    #有多少页
	#生成所有相册页面，还好都是有规律的。汗|||
	page_list = [r'http://my.hupu.com%s%d.html' %(path,i) for i in xrange(1,P_max+1)]
	#print page_list #output
	return page_list

def get_content(url):
	content = urllib2.urlopen(url).read()
	print '%s  ---page done!' %url
	return content


def get_urls(content):
	pat = r'http://i[\d]{1}\.hoopchina\.com\.cn/.+small\.(?:jpg|gif|png|jpeg)'
	url_list = re.findall(pat,content)    #parse img url
	print '得到%d张图片' %len(url_list)
	urls = '\n'.join(url_list)
	urls = re.sub(r'small\.',r'big.',urls)
	return urls

def dowm_img(urls):
	pass

def main():
	#脚本可带url参数
	if len(sys.argv)<=1:
		home = r'http://my.hupu.com/jzgk/photo/a74456-1.html'    #脚本内置虎扑相册地址
	else:
		home = sys.argv[1]
	homepage = urllib2.urlopen(home).read()    #.decode('gb2312').encode('utf-8')
	title    = re.search(r'<title>(.+)</title>',homepage).group(1)
	print '正在抓取-%s-相册' %title
	page_list = get_pages(home,homepage)    #得到相册的所有页面
	content = ''
	for i in page_list:
		content +=get_content(i)     #得到所有页面内容
	#print content
	urls = get_urls(content)
	#print urls
	os.system(r'mkdir "%s" ' %title)
	print r'创建"%s"文件夹成功' %title
	url_file = open(r'%s/urls' %title,'w')    #追加:w+
	try:
		url_file.write(urls)
		print '图片url写入成功'
	finally:
		url_file.close()
	#os.system('wget %s' %urls)

if __name__ == '__main__':
    main()
