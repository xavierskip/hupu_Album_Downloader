#!/usr/bin/env python
#coding: GBK
#version: 0.2
import os,sys,urllib2,re

def get_pages(home,path):
	homepage = get_content(home)
	title    = re.search(r'<title>(.+)</title>',homepage).group(1)
	print '正在抓取相册>>>%s>>>' %title
	pat  = path+ r'-([\d]+).html(?:\'|\")>'       #匹配剩下的相册页面
	P_nums = re.findall(pat,homepage)
	if P_nums==[]:
		page_list = [home]
		return page_list,title
	else:
		P_max = int(P_nums[-1])
		#生成所有相册页面，还好都是有规律的。汗|||
		page_list = [r'http://my.hupu.com%s-%d.html' %(path,i) for i in xrange(1,P_max+1)]
		return page_list,title

def get_urls(content):
	pat = r'http://i[\d]{1}\.hoopchina\.com\.cn/.+small\.(?:jpg|gif|png|jpeg|bmp)'
	url_list = re.findall(pat,content)    #parse img url
	# sub smell to big pic and remove repeat img url
	# list(set(url_list))
	urls = []
	for i in url_list:
		if not i in urls:
			urls.append(i)
	return re.sub(r'small.', r'big.', '\n'.join(urls)),len(urls)

def get_content(url):
	return urllib2.urlopen(url).read()

def dowm_img(urls,path,pic_num):
	num = 0
	for url in urls.split('\n'):
		filename = url.split('/')[-1]
		print '[%s/%s]download>>>%s' %(num,pic_num,filename)
		data = get_content(url)
		f= open('%s/%s' %(path,filename),'wb')
		f.write(data)
		f.close()
		num+=1

def main():
	#脚本可带url参数
	if len(sys.argv)<=1:
		print '请输入需要下载的相册地址。'
		home = r'http://my.hupu.com/sunyatsen/photo/a135716.html'    #福利
	else:
		home = sys.argv[1]
	# 判断url是否正确
	match = re.match(r'http://my\.hupu\.com(/[\S]+?/photo/a[\d]+?)(?:\-[\d]+\.html|\.html)',home) 
	if match == None:
		print '此URL不能识别\n请输入单个相册的页面地址！'
		exit()
	path = match.group(1)    #Album path
	print '\n','='*10,'开始抓取','='*10,'\n'
	#得到相册的所有页面地址
	page_list,title = get_pages(home,path)
	P_num =  len(page_list)
	print '此相册有%d页！' %P_num
	content = ''
	current = 0
	for i in page_list:
		current +=1
		content +=get_content(i)
		print '%d/%d:page done:%s' %(current,P_num,i)
	#从所有的页面内容中抓取图片url
	urls,pic_num = get_urls(content)
	os.system(r'mkdir "%s" ' %title)
	print '%s张图片需要下载\n创建"%s"文件夹>>>' %(pic_num, title)
	with open(r'%s/urls' %title,'w') as urls_file:
		urls_file.write(urls)
		print '图片url写入文件成功'
	print '\n','='*10,'开始下载','='*10,'\n'
	end = os.system(r'wget -N -i "%s/urls" -P "%s" ' %(title,title) ) # if you have wget
	if end == 1:
	    dowm_img(urls,title,pic_num)
	else:
	    print 'wget搞定!'
		
if __name__ == '__main__':
    main()
