#!/usr/bin/env python
# coding: utf-8
from threading import Thread
from hashlib import md5
from math import ceil
import ConfigParser
import requests
import os
import re
import getpass
# import ipdb

HERE = os.path.dirname(os.path.abspath(__file__))
CookieFile = "cookies.conf"
COOKIES = os.path.join(HERE, CookieFile)


def enter_name_pwd():
    name = raw_input('username:')
    pwd = getpass.getpass()
    return name, pwd


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
        self.first_page = ''  # the first get page
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
            # unknow=-1 init|empty=0 succeed=1
            self.state = -1
        # private=302 login_fail=403 encrypt=501
        self.state = 0
        # requests session
        self.session = requests.session()
        self.g = ''
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2357.81 Safari/537.36'
        }
        self.session.headers.update(**headers)
        self.login_page = 'https://passport.hupu.com/pc/login?project=www&from=pc'
        self.login_url = 'https://passport.hupu.com/pc/login/member.action'


    def get(self, url, cookies):
        """ used to get page content
        """
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

    def get_cookie(self, payload):
        self.session.get(self.login_page)  # get some cookie
        r = self.session.post(self.login_url, payload)
        json = r.json()
        if json['code'] != 1000:
            print(json['msg'])
        cookies = r.cookies
        must_key = ['u','ua','us']
        cookie_keys = cookies.keys()
        for k in must_key:
            if k not in cookie_keys:
                return False
        for k in cookie_keys:  # or must_key
            self.cookieconfig.set(payload['username'], k, cookies.get(k))
        self.cookieconfig.save()
        return cookies

    def login(self, user, password):
        """try to login and update the cookie
        """
        def _try_get(this, url, cookies):
            this.first_page = this.get(url, cookies)
            if this.first_page:
                this.g += this.first_page
                return True
            else:
                return False

        def _get_new_cookie(this, user, password=''):
            if not password:  # if you don't pass the password, sould enter it manually
                user, password = enter_name_pwd()
            data = {
                'username': user,
                'password': md5(password).hexdigest()
            }
            new_cookie = this.get_cookie(data)
            if new_cookie:
                return _try_get(this, this.homepage, new_cookie)
            else:
                this.cookieconfig.remove(user)
                self.state = 403  # change self.state
                return False

        self.cookieconfig = Cookie()
        if self.cookieconfig.has_user(user):
            cookie = self.cookieconfig.getcookies(user)
            result = _try_get(self, self.homepage, cookie)
            if result:
                return result
            else:
                if self.state == 403:  # maybe cookie expired and get new one
                    return _get_new_cookie(self, user, password)
                else:  # you can't login in
                    return False
        else:
            return _get_new_cookie(self, user, password)

    def get_info(self):
        page = self.first_page
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
