#!/usr/bin/env python
#coding: utf-8
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
	u_str = ' '.join(url_list)
	u_str = re.sub('small\.','big.',u_str)
	return u_str

def dowm_img(urls):
	pass

def main():
	#home = sys.argv[1]
	home = r'http://my.hupu.com/McGrady1jia/photo/a81209-1.html'
	homepage = urllib2.urlopen(home).read()
	page_list = get_pages(home,homepage)
	content = ''
	for i in page_list:
		content +=get_content(i)
	#print content
	U_list = url_list(content)
	urls = tourls(U_list)
	print urls
	#os.system('wget %s' %urls)

if __name__ == '__main__':
    main()
