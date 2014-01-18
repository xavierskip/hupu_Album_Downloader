#!/usr/bin/env python
#coding: utf-8
import os,sys
from HupuAlbum import Album

def dowm_img(urls,title,pic_num):
    num = 0
    for url in urls.split('\n'):
        filename = url.split('/')[-1]
        print '[%s/%s]download>>>%s' %(num,pic_num,filename)
        data = get_content(url)
        f= open('%s/%s' %(title,filename),'wb')
        f.write(data)
        f.close()
        num+=1

def main():
    weal = 'http://my.hupu.com/sunyatsen/photo/a135716.html'
    if len(sys.argv)<=1:
        url = 'http://my.hupu.com/sunyatsen/photo/a135716.html'    #福利
        print '是否下载此相册[%s]?\n按任意键继续\n否则Ctrl+c退出' %weal
        raw_input()
    else:
        url = sys.argv[1]
    album = Album(url)
    # path meets
    if album.detect_path():
        pass
    else:
        print '此URL不能识别\n请输入单个相册的页面地址！'
        print 'url should be like this: %s' %weal
        return 0
    if album.get_info():
        pass
    else:
        print "请确认，在没有登陆的情况下依旧可以访问此相册吗？"
        return 0
    print '《%s》----此相册有%d页%d张\n抓取中......' %(album.title,album.hasPages,album.hasPics)
    album.get_imgs()
    print '抓取到%d张图片地址' %album.getPics
    print '创建"%s"文件夹' %album.title
    os.system(r'mkdir "%s" ' %album.title)
    with open(r'%s/urls' %album.title,'w') as urls_file:
        urls_file.write(album.imgUrls)
        print '图片url写入完成'
    wget = os.system(r'wget -N -i "%s/urls" -P "%s" ' %(album.title,album.title) ) # if you have wget
    if wget == 1:
        dowm_img(album.imgUrls,album.title,album.getPics)
    return 1

if __name__ == '__main__':
     main() 