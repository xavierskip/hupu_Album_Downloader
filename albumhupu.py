#!/usr/bin/env python
# coding: utf-8
from hupu import HupuAlbum, detect_album_path, Cookie, enter_name_pwd
import urllib2
import sys
import os
import argparse
# import ipdb
"""
# 普通        http://my.hupu.com/hoopchinalv/photo/a1787001.html
# 只对好友公开 http://my.hupu.com/BelieveMyself/photo/a139390-1.html
# 加密        http://my.hupu.com/BelieveMyself/photo/a100107-1.html
# 由来        http://my.hupu.com/sunyatsen/photo/a135716.html
# 空白测试     http://my.hupu.com/137262/photo/a0-1.html
"""

parser = argparse.ArgumentParser(description='download hupu.com album images')
parser.add_argument("url", help="hupu album url", type=str)
parser.add_argument("-p", nargs=2, metavar=('username', 'password'), help="hupu.com username and password")
Args = parser.parse_args()


def filter_path_char(s):
    illegal_chars = {
        '/': '-'
    }
    for k, v in illegal_chars.iteritems():
        s = s.replace(k, v)
    return s


def save_imgs(urls, path, n):
    c = 1
    for url in urls.split('\n'):
        filename = url.split('/')[-1]
        print('[%s/%s]download>>>%s' % (c, n, url))
        img = urllib2.urlopen(url).read()
        f = os.path.join(path, filename)
        with open(f, 'wb') as fp:
            fp.write(img)
        c += 1


def get_album(url, username='', password=''):
    url = detect_album_path(url)
    if not url:
        print('此URL不能识别\n请输入单个相册的页面地址！')
        return None
    if not username:
        cookie = Cookie()
        try:
            username = cookie.config.sections()[0]
        except IndexError:
            username, password = enter_name_pwd()
        del cookie
    album = HupuAlbum(url)
    if album.login(username, password):
        print("登录成功")
    else:
        tips = {
            302: "请确认登录用户可以访问此相册吗？",
            403: "登陆失败，请检查用户名和密码",
            501: "暂不支持加密相册"
        }
        print(tips[album.state])  # tips
        return None
    # get album info
    info = album.get_info()
    album.title = album.title.encode('utf-8')  # str encode
    if info.state == 0:
        print("《%s》是空相册抓不到图片" % album.title)
        print(album.homepage)
        return None
    else:
        print('《%s》此相册有%d张、%d页' % (album.title, album.pics, album.pages))
        album.down()
        print('抓取到%d张图片' % album.get_pics)
        return album


def main():
    if Args.p:
        username, password = Args.p
    else:
        username = ''
        password = ''
    album = get_album(Args.url, username, password)
    # down album img
    if album:
        try:
            foldername = filter_path_char(album.title)
            print('创建"%s"文件夹' % foldername)
            os.mkdir(foldername)
        except OSError as e:
            print('创建文件夹失败')
            raise e
        urls_file = os.path.join(foldername, 'urls')
        with open(urls_file, 'w') as f:
            f.write(album.pics_urls)
            print('图片url写入完成')
        print('{}{}{}'.format('=' * 10, '开始下载图片', '=' * 10))
        wget = os.system('wget -N -i "%s" -P "%s" ' % (urls_file, foldername))
        if wget == 1:  # if you don't have wget
            save_imgs(album.pics_urls, foldername, album.get_pics)
        return 1
    else:
        return 0


if __name__ == '__main__':
    main()
