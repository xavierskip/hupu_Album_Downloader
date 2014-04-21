#!/usr/bin/env python
#coding: utf-8
import re
import requests
from math import ceil
from threading import Thread

def detect_album_path(album_url):
    match = re.match('http://my\.hupu\.com(/[\S]+?/photo/a[\d]+?)(?:\-[\d]+\.html|\.html)',album_url)
    if match:
        path = match.group(1)
        homepage = 'http://my.hupu.com%s.html' %path
        return homepage
    else:
        return 0


class HupuAlbum(object):
    # global
    g = ''
    session = requests.session()
    def __init__(self, url):
        self.url = url
        # Album info
        self.title = ''
        self.cover = ''
        self.pics = 0
        self.pages = 0
        self.page_urls = []
        # Album pics
        self.get_pics = 0
        self.pics_urls = ''
        # Album path
        match = re.match('http://my\.hupu\.com(/[\S]+?/photo/a[\d]+?)(?:\-[\d]+\.html|\.html)',self.url)
        if match:
            self.path = match.group(1)
        # empty:0 init:1  access:200 deny：302
        self.stat = 1

    def login(self,username,password):
    	login = "http://passport.hupu.com/login"
        data = {
        'username': username,
        'password': password,
        'remember': 1
        }
        r = self.session.post(login,data)
        cookies = r.cookies
        try:
            cookies['ua'] and cookies['u']
        except KeyError:
            return None
        else:
            return self

    def get_info(self):
    	r = self.session.get(self.url)
        # can visit the album
        if len(r.history) > 0 and r.history[0].status_code == 302:
            self.stat = 302
            return self
        # charset
        if r.encoding == 'gb2312':
            page = r.content.decode('gbk')#.encode('utf-8')
        else:
            page = r.content
        # get album title
        title = re.search('<title>(.+)</title>',page)
        if title:
            self.title = title.group(1)
        # album cover
        cover = re.search('class="cover"><img src="(.+?)"',page)
        if cover:
            self.cover = cover.group(1)
        # get album pic num
        pics = re.search(u'共(\d+)张照片',page)
        if pics:
            self.pics = int(pics.group(1))
        # album page num
        self.pages = int(ceil(self.pics/60.0))
        # album page list
        self.page_urls = ['http://my.hupu.com%s-%d.html' %(self.path,i) for i in range(1,self.pages+1)]
        # album empty
        if self.pics == 0:
            self.stat = 0
            return self
        self.stat = 200
        return self

    def down(self):
        # get_pages with threads
        threads = []
        for url in self.page_urls:
            t = self.GetUrlThread(url)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        # filter img
        img_list = re.findall('<span>.+?<img src="(.+?)"',self.g)
        self.get_pics = len(img_list)
        self.pics_urls = re.sub('small.', 'big.', '\n'.join(img_list))
        return self.pics_urls

    def save(self):
        self.get_info()
        self.down()
        return self

    # Thread
    class GetUrlThread(Thread):
        def __init__(self, url):
            self.url = url
            super(HupuAlbum.GetUrlThread, self).__init__()
     
        def run(self):
            print('down: %s' %self.url)
            response = HupuAlbum.session.get(self.url)
            HupuAlbum.g += response.content # global g