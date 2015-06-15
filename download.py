#!/usr/bin/env python
#coding: utf-8
import os,sys
import re
import urllib2
from hupu import HupuAlbum
from hupu import detect_album_path
# 普通        http://my.hupu.com/hoopchinalv/photo/a1787001.html
# 只对好友公开 http://my.hupu.com/BelieveMyself/photo/a139390-1.html
# 加密        http://my.hupu.com/BelieveMyself/photo/a100107-1.html
# 由来        http://my.hupu.com/sunyatsen/photo/a135716.html
# 空白测试     http://my.hupu.com/137262/photo/a0-1.html
# import ipdb

def save_imgs(urls,path,n):
    c=1
    for url in urls.split('\n'):
        filename = url.split('/')[-1]
        print '[%s/%s]download>>>%s' %(c,n,url)
        img = urllib2.urlopen(url).read()
        with open('%s/%s' %(path,filename),'wb') as f:
            f.write(img)
        c+=1

def get(url, username, password):
    url = detect_album_path(url)
    if url:
        album = HupuAlbum(url)
        # login
        if album.login(username, password):
            print "登录成功"
        else:
            tips = {
                302: "请确认登录用户可以访问此相册吗？",
                403: "登陆失败，请检查用户名和密码",
                501: "暂不支持加密相册"
            }
            print tips[album.state] # tips
            return None
        # get album info
        info = album.get_info()
        album.title = album.title.encode('utf-8') # str encode
        if info.state == 0:
            print "《%s》是空相册抓不到图片" %album.title
            print album.homepage
            return None
        else:            
            print '《%s》此相册有%d张、%d页' %(album.title,album.pics,album.pages)
            album.down()
            print '抓取到%d张图片' %(album.get_pics)
            return album
    else:
        print '此URL不能识别\n请输入单个相册的页面地址！'
        return None


def main():
    useage = 'Usage: python download.py <url> <username> <password>'
    try:
        url = sys.argv[1]
        username = sys.argv[2]
        password = sys.argv[3]
    except IndexError, e:
        print useage
        return None
    album = get(url, username, password)
    # down album img
    if album:
        try:
            print '创建"%s"文件夹' %album.title
            os.system('mkdir "%s" ' %album.title)
        except Exception, e:
            print '创建文件夹失败'
            raise e
        with open('%s/urls' %album.title,'w') as f:
            f.write(album.pics_urls)
            print '图片url写入完成'
        print '='*10,'开始下载图片','='*10
        wget = os.system('wget -N -i "%s/urls" -P "%s" ' %(album.title,album.title) ) # if you have wget
        if wget == 1:
            path = '%s/' %album.title
            save_imgs(album.pics_urls,path,album.get_pics)
        return 1
    else:
        return 0

if __name__ == '__main__':
    main()