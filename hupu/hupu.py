#!/usr/bin/env python
# coding: utf-8
import re
import requests
from math import ceil
from threading import Thread
import ConfigParser
# import ipdb
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CookieFile = "cookies.conf"
COOKIES = os.path.join(HERE, CookieFile)


def detect_album_path(album_url):
    match = re.match('http://my\.hupu\.com(/[\S]+?/photo/a[\d]+?)(?:\-[\d]+\.html|\.html)', album_url)
    if match:
        path = match.group(1)
        homepage = 'http://my.hupu.com%s.html' % path
        return homepage
    else:
        return False


class HupuAlbum(object):
    # g = ''
    # session = requests.session()
    def __init__(self, url):
        self.url = url
        # Album info
        self.title = ''
        self.cover = ''  # cover img url
        self.pics = 0
        self.pages = 0
        self.page_urls = []
        # Album info acquired
        self.get_pics = 0
        self.pics_urls = ''
        # Album path
        match = re.match('http://my\.hupu\.com(/[\S]+?/photo/a[\d]+?)(?:\-[\d]+\.html|\.html)', self.url)
        if match:
            self.path = match.group(1)
            self.homepage = 'http://my.hupu.com%s.html' % self.path
        else:
            self.state = -1
        # unknow=-1 init|empty=0 succeed=1
        # private=302 login_fail=403 encrypt=501
        self.state = 0
        # requests session
        self.session = requests.session()
        self.g = ''
        headers = {
            # 'Host': 'passport.hupu.com',
            # 'Origin': 'http://passport.hupu.com',
            # 'Referer': 'http://passport.hupu.com/login',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36'
        }
        self.session.headers.update(**headers)

    def get(self, url, cookies):
        ''' set requests.session cookies and headers
        '''
        self.session.cookies.clear()  # CookieConflictError: There are multiple cookies with name
        self.session.cookies.update(cookies)
        r = self.session.get(url)
        if len(r.history) > 0 and r.history[0].status_code == 302:
            self.state = 302  # 相册内容不公开
            return False
        elif re.search(u'很抱歉，当前页面正在维护中，请稍后再来', r.text):
            self.state = 403  # 登录失败
            return False
        elif re.search(u'你输入的密码错误，请重新输入', r.text):
            self.state = 501  # 暂不支持加密相册
            return False
        else:
            self.state = 1
            return r.text

    def getCookie(self, url, payload):
        r = self.session.post(url, payload)
        cookies = r.cookies
        if cookies.get('u') and cookies.get('ua'):
            for k in ['u', 'ua']:
                self.cookieconfig.set(payload['username'], k, cookies.get(k))
            self.cookieconfig.save()  # save cookie
            return cookies
        else:
            self.state = 403  # 登录失败
            return False

    def login(self, user, password):
        login = "http://passport.hupu.com/login"
        payload = {
            'username': user,
            'password': password,
            'rememberme': 1,
            'charset': 'utf-8',
            'jumpurl': '/',
            'mode': 'email'
        }
        self.cookieconfig = Cookie()
        if self.cookieconfig.has_user(user):
            loginCookie = self.cookieconfig.getcookies(user)
            self.content = self.get(self.homepage, loginCookie)
            if self.content:
                self.g += self.content  # album first page
                return True
            else:
                if self.state == 403:  # expired cookie then login fail
                    loginCookie = self.getCookie(login, payload)
                    if not loginCookie:
                        self.cookieconfig.remove(user)
                        return False  # login fail
                        # if get cookie than skip the judgment
                else:
                    # login succeed but can't access the album
                    return False
        else:
            loginCookie = self.getCookie(login, payload)
            if not loginCookie:
                return False  # login fail
                # if get cookie than skip the judgment
        self.content = self.get(self.homepage, loginCookie)
        if self.content:
            self.g += self.content
            return True
        else:
            return False

    def get_info(self):
        page = self.content
        # get album title
        title = re.search('<title>(.+)</title>', page)
        if title:
            self.title = title.group(1)
        # album cover
        cover = re.search('class="cover"><img src="(.+?)"', page)
        if cover:
            self.cover = cover.group(1)
        # get album pic num
        pics = re.search(u'共(\d+)张照片', page)
        if pics:
            self.pics = int(pics.group(1))
        # album page num
        self.pages = int(ceil(self.pics / 60.0))
        # album page list
        self.page_urls = ['http://my.hupu.com%s-%d.html' % (self.path, i) for i in range(1, self.pages + 1)]
        # album empty
        if self.pics == 0:
            self.state = 0  # empty album
            return self
        else:
            self.state = 1
            return self

    def down(self):
        # get all album page content with threads
        threads = []
        # skip the first page because it be taken when login
        for i in range(1, len(self.page_urls)):
            t = GetUrlThread(self, self.page_urls[i])
            threads.append(t)
            t.start()
        for t in threads:
            t.join(timeout=20)
        # filter img
        img_list = re.findall('<span>.+?<img src="(.+?)"', self.g)
        self.get_pics = len(img_list)
        self.pics_urls = re.sub('small.', 'big.', '\n'.join(img_list))
        # clear g ! important !!! 
        # HupuAlbum.g = ''
        return self.pics_urls

    def save(self):
        self.get_info()
        self.down()
        return self


# Thread
class GetUrlThread(Thread):
    def __init__(self, cls, url):
        self.url = url
        self.cls = cls
        self.session = cls.session
        super(GetUrlThread, self).__init__()

    def run(self):
        response = self.session.get(self.url)
        self.cls.g += response.text


class Cookie(object):
    def __init__(self):
        super(Cookie, self).__init__()
        self.file = COOKIES
        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.file)

    def __exit__(self):
        self.save()

    def set(self, section, k, v):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, k, v)

    def remove(self, section):
        self.config.remove_section(section)
        self.save()

    def save(self):
        self.config.write(open(self.file, "w"))

    def get(self, section, key):
        return self.config.get(section, key)

    def has_user(self, user):
        return self.config.has_section(user)

    def getcookies(self, section):
        return dict(self.config.items(section))

        # class loginError(Exception):
        #     def __init__(self, value):
        #         self.value = value
        #     def __str__(self):
        #         return repr(self.value)
