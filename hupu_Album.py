#!/usr/bin/env python
#coding: utf-8
import os,sys,urllib2,re

def get_pages(url):
	return page_list

def get_content(url):
	content = urllib2.urlopen(url).read()
	print 'page done! %s' %url
	return content

def url_list(content):
	pat = 'http://i[\d]{1}\.hoopchina\.com\.cn/.+small\.(?:jpg|gif|png|jpeg)'
	url_list = re.findall(pat,content)
	return url_list

def urls(url_list):
	
	urls = ' '.join(url_list)
	urls = re.sub('small\.','big.',urls)
	return urls
	return urls

def dowm_img(urls):
	pass

def main():
	page_list = get_pages(sys.argv[1])
	for i in page_list:
		content +=get_content(i)
	url_list = url_list(content)
	urls = urls(url_list)
	#os.system('wget %s' %urls)

if __name__ == '__main__':
    main()
