#!/usr/bin/env python
#coding: utf-8
import urllib2
import re
from math import ceil

def get_content(url):
    ua = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31'
    req = urllib2.Request(url,headers={'User-Agent':ua})
    return urllib2.urlopen(req).read()



class Album(object):
    """docstring for Album"""
    def __init__(self, url):
        self.url = url
        # self.img_pat = r'http://i[\d]{1}\.hoopchina\.com\.cn/.+small\.(?:jpg|gif|png|jpeg|bmp)'
        self.img_pat = r'http://i[\d]{1}\.hoopchina\.com\.cn/.+small\.[\w]+'
        # info
        self.path = ''
        self.homepage = ''
        self.title = ''
        self.cover = ''
        self.hasPics = 0
        self.hasPages = 0
        self.getPages = 0
        self.getPics = 0
        self.imgUrls = ''
        # 0:init 1:success 2:incorrect url 3:no access
        self.stat = 0 

    def detect_path(self):
        match = re.match(r'http://my\.hupu\.com(/[\S]+?/photo/a[\d]+?)(?:\-[\d]+\.html|\.html)',self.url)
        if match:
            self.path = match.group(1)
            self.homepage = 'http://my.hupu.com%s.html' %self.path
            #print self.homepage
            return 1
        else:
            # math == None
            return 0

    def get_info(self):
        # page = get_content(self.url)
        page = get_content(self.url).decode('gbk') #字符编码呀！
        cover = self.get_cover(page)
        try:
            self.cover = cover[0]
        except Exception, e:
            return 0
        self.title = re.search(r'<title>(.+)</title>',page).group(1)
        pics_pat = u'共(\d+)张照片'
        self.hasPics = int(re.findall(pics_pat,page)[0])
        self.hasPages = int(ceil(self.hasPics/60.0))
        self.page_list = [r'http://my.hupu.com%s-%d.html' %(self.path,i) for i in range(1,self.hasPages+1)]
        self.getPages = len(self.page_list)
        return self.page_list

    def get_imgs(self):
        # 抓取网页中图片列表部分
        web_part = ''
        for p in self.page_list:
            c = get_content(p)
            tmp = self.single_page_albumlist(c)
            # print p,':',len(re.findall(self.img_pat,tmp))
            web_part += tmp
        # 再一起抓取出其中的图片地址
        img_list = re.findall(self.img_pat,web_part)
        # small img to big img
        self.imgUrls = re.sub(r'small.', r'big.', '\n'.join(img_list))
        self.getPics = len(img_list)
        return self.getPics

    def get_cover(self,page):
        cover_pat = r'cover.+(%s)' %self.img_pat
        cover_url = re.findall(cover_pat,page)
        return cover_url

    def single_page_albumlist(self,page_content):
        albumlist_pat = r'<div class="albumlist_list">([\s\S]*?)</ul>'
        return re.search(albumlist_pat,page_content).group()

    ### 
    def save(self):
        if self.detect_path():
            pass
        else:
            self.stat = 2
            return 0
        if self.get_info():
            pass
        else:
            self.stat = 3
            return 0
        self.get_imgs()
        self.stat = 1
        return 1
