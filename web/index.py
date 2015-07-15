#-*- coding:utf-8 -*-
from flask import g,request,jsonify,abort,session,make_response
from flask import render_template,redirect,url_for
from flask import Response
#
from hupu import HupuAlbum
from hupu import detect_album_path
#
from datetime import timedelta
from math import ceil
import os,base64,json
import requests
import time
import re
import sys
#
from db import Database
from web import app
# import ipdb
# weibo login
APPKEY = app.config.get('APPKEY')
APPSECRET = app.config.get('APPSECRET')
REDIRECTURI = app.config.get('REDIRECTURI')
# VAR
LASTDATE = app.config.get('LASTDATE')
LUSER = app.config.get('LUSER')
LPWD = app.config.get('LPWD')
# set secret_key
# SECRETKEY = app.config.get('SECRETKEY')
# app.secret_key = SECRETKEY

def img_base64(img,ext):
    return 'data:image/%s;base64,%s' %(ext,base64.b64encode(img))

def pagination(currentpage, pagenums, ripple):
    rangeStart, rangeEnd = currentpage-ripple,currentpage+ripple
    if rangeStart <= 1+1 and rangeEnd >= pagenums-1:
        pages = [ i for i in range(1,pagenums+1)]
    elif rangeStart <=1+1 and  rangeEnd < pagenums-1:
        pages = [ i for i in range(1,rangeEnd+1)]
        pages.extend(['',pagenums])
    elif rangeStart > 1+1 and rangeEnd >= pagenums-1:
        pages = [1,'']
        pages.extend([ i for i in range(rangeStart,pagenums+1)])
    else:
        pages = [1,'']
        pages.extend([i for i in range(rangeStart,rangeEnd+1)])
        pages.extend(['',pagenums])
    return pages

@app.before_request
def before_request():
    session.permanent = True
    g.db = Database(
        host = app.config.get('HOST'),
        port = app.config.get('PORT'),
        user = app.config.get('DBUSER'),
        passwd = app.config.get('DBPASSWD'),
        db = app.config.get('DB')
    )
    g.cur = g.db.cur

@app.teardown_request
def teardown_request(exception):
    if hasattr(g,'db'):
        g.db.close()

# method
@app.route('/getalbum', methods=['POST'])
def get():
    start = time.time()
    url = request.form['url']
    if not detect_album_path(url):
        return jsonify(state = -1)
    user,pwd = LUSER,LPWD
    uid = session.get('uid')
    if uid:
        g.cur.execute("""SELECT `uid` FROM `users` where `uid` = %s""",(uid,))
        if g.cur.fetchone():
            user = request.form.get('user')
            pwd = request.form.get('password')
            if not user or not pwd :
                user,pwd = LUSER,LPWD
        else:
            return jsonify(state = 4) # uid non-existent
    # get pics
    album = HupuAlbum(url)
    if not album.login(user,pwd):
        return jsonify(state = album.state)
    album.save()
    coverimg='' # album.cover img to base64
    if album.state==1:
        # return cover img with base 64 and store data
        # cover = album.session.get(album.cover).content
        # ext = album.cover.split('.')[-1]
        # coverimg = img_base64(cover,ext)
        coverimg = album.cover
        g.cur.execute(''' INSERT INTO  `albums` (`url`,`title`,`cover`,`pics`,`getPics`,`picsUrls`) VALUES (%s,%s,%s,%s,%s,%s)\
            ON DUPLICATE KEY UPDATE `title`=%s,`cover`=%s,`pics`=%s,`getPics`=%s,`picsUrls`=%s,`times`=`times`+1 ''',
            (album.homepage,album.title,coverimg,album.pics,album.get_pics,album.pics_urls,
                album.title,coverimg,album.pics,album.get_pics,album.pics_urls))
        g.db.commit()
    return jsonify(
        state = album.state,
        homepage = album.homepage,
        title = album.title,
        cover = coverimg,
        pics = album.pics,
        get_pics = album.get_pics,
        pics_urls = album.pics_urls,
        time = time.time()-start
    )

@app.route('/getalbum', methods=['GET'])
def getalbum():
    url = request.args.get('url')
    if url:
        g.cur.execute(''' SELECT `picsUrls`,`title` FROM `albums` WHERE `url` = %s''',(url,))
        r = g.cur.fetchone()
        if r:
            # return Response(r.get('picsUrls'),mimetype='text/pain')
            title = r.get('title').encode('utf-8')
            # print title.decode('utf-8'),type(title)
            return Response(r.get('picsUrls'),
                headers = {
                    'Content-Type': 'text/pain; charset=utf-8',
                    'Content-Disposition': 'attachment; filename="%s.txt"' %title
                })
        else:
            return 'don\'t found!'
    else:
        return abort(400)

@app.route('/zip', methods=['GET'])
def zip():
    '''
    need nginx module mod_zip  https://github.com/evanmiller/mod_zip
    '''
    url = request.args.get('url')
    if url:
        g.cur.execute(''' SELECT `title`,`picsUrls` FROM `albums` WHERE `url` = %s''',(url,))
        r = g.cur.fetchone()
        if r:
            title = r.get('title').encode('utf-8')
            files = r.get('picsUrls').split('\n')
            fileList = []
            for f in files:
                name = f.split('/')[-1]
                # url = 'http://t.vm'+url_for('static', filename=f)
                path = '/img/'+re.split('/',f,3)[-1]
                resp = requests.head(f)
                size = resp.headers.get('content-length')
                fileList.append(' '.join(['-',size,path,name]))
            fs = "\n".join(fileList)
            # print fs
            return Response(fs,
                    headers={
                        'X-Archive-Files': 'zip',
                        'Content-Disposition': 'attachment; filename="%s.zip"' %title
                    }
                )
        else:
            return abort(404)
    else:
        return abort(400)

    # return "zip"  

# weibo registry
@app.route('/oauth')
def oauth():
    authorize = 'https://api.weibo.com/oauth2/authorize?client_id=%s&response_type=code&redirect_uri=%s' \
        %(APPKEY,REDIRECTURI)
    return redirect(authorize)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        abort(400)
    access_token = 'https://api.weibo.com/oauth2/access_token?client_id=%s&client_secret=%s&grant_type=authorization_code&redirect_uri=%s&code=%s' \
        %(APPKEY,APPSECRET,REDIRECTURI,code)
    r = requests.post(access_token)
    data = json.loads(r.content)
    try:
        access_token = data[u'access_token']
        uid = int(data[u'uid'])
        expire = int(data[u'expires_in'])
    except KeyError:
        return 'no keys!<a href="/">return back</a>'
    usershow = 'https://api.weibo.com/2/users/show.json?access_token=%s&uid=%s' %(access_token,uid)
    r = requests.get(usershow)
    info = json.loads(r.content)
    name        = info[u'name']
    avatar      = info[u'profile_image_url']
    province    = info[u'province']
    city        = info[u'city']
    location    = info[u'location']
    description = info[u'description']
    blog        = info[u'url']
    gender      = info[u'gender']
    followers   = info[u'followers_count']
    friends     = info[u'friends_count']
    statuses    = info[u'statuses_count']
    created     = info[u'created_at']
    avatar_hd   = info[u'avatar_hd']
    g.cur.execute("""REPLACE INTO  `users` (`uid`,`access_token`,`name`,`avatar`,`province`,`city`,`location`,`description`,`blog`,`gender`,`followers`,`friends`,`statuses`,`created`,`avatar_hd`)\
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(uid,access_token,name,avatar,province,city,location,description,blog,gender,followers,friends,statuses,created,avatar_hd))
    g.db.commit()
    # cookie expire
    # app.permanent_session_lifetime = timedelta(seconds=expire)
    session['uid'] = uid
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session['uid'] = ''
    return redirect(url_for('index'))

# views 
@app.route('/')
def index():
    uid = session.get('uid')
    if uid:
        g.cur.execute("""SELECT `name`,`avatar`  FROM `users` WHERE `uid` = %s""",(uid,))
        f = g.cur.fetchone()
        if f:
            user = {
                'name': f.get('name'),
                'avatar': f.get('avatar')
            }
            return render_template('advance.html',user=user,lastDate=LASTDATE)
    else:
        return render_template('home.html',lastDate=LASTDATE)

def selectLIMIT(request):
    imgInOnepage = 60.0# how much img in one page , float num
    try:
        current  = int(request.args.get('page'))-1
        if current < 0:
            raise TypeError
    except TypeError as e:
        current = 0 # currentpage start by 0
    return current,int( current*imgInOnepage ),int(imgInOnepage)

def selectUrls(urls, offset, row_count):
    stmt = ''' SELECT url,title,cover,pics,getPics,times FROM albums WHERE url IN (%s) '''\
        %(','.join(['%s' for i in range(len(urls))])) + 'LIMIT %s,%s' %(offset, row_count)
    g.cur.execute( stmt,urls)
    return [dict(url=row.get('url'),title=row.get('title'),cover=row.get('cover'),pics=row.get('pics'),getPics=row.get('getPics'),times=row.get('times')) \
                for row in g.cur.fetchall() ]


@app.route('/albums/')
def albums():
    currentpage, offset, row_count = selectLIMIT(request)
    g.cur.execute(''' SELECT url,title,cover,pics,getPics,times FROM albums order by logTime desc LIMIT %s,%s''',(offset, row_count))
    albums = [dict(url=row.get('url'),title=row.get('title'),cover=row.get('cover'),pics=row.get('pics'),getPics=row.get('getPics'),times=row.get('times')) \
                for row in g.cur.fetchall() ]
    g.cur.execute('''SELECT count(*) from `albums`''')
    pagenums = int( ceil( int( g.cur.fetchone().get('count(*)') ) / float(row_count) ))
    nav = pagination(currentpage, pagenums, 2) # pagination
    return render_template('albums.html', albums=albums, nav=nav, currentpage=currentpage+1, func=sys._getframe().f_code.co_name)

@app.route('/SD/')
def sd():
    currentpage, offset, row_count = selectLIMIT(request)
    album_urls = [
        'http://my.hupu.com/3616496/photo/a75782.html',
        'http://my.hupu.com/3616496/photo/a1820422.html',
        'http://my.hupu.com/3616496/photo/a1818729.html',
        'http://my.hupu.com/3616496/photo/a168403.html',
        'http://my.hupu.com/3616496/photo/a156657.html',
        'http://my.hupu.com/3616496/photo/a144107.html',
        'http://my.hupu.com/3616496/photo/a1820478.html',
        'http://my.hupu.com/3616496/photo/a1820479.html',
        'http://my.hupu.com/3616496/photo/a1793673.html',
        'http://my.hupu.com/3616496/photo/a70797.html',
        'http://my.hupu.com/3616496/photo/a63846.html',
        'http://my.hupu.com/3616496/photo/a50764.html',
        'http://my.hupu.com/3616496/photo/a1820550.html',
        'http://my.hupu.com/3616496/photo/a1820551.html',
        'http://my.hupu.com/3616496/photo/a73465.html',
        'http://my.hupu.com/3616496/photo/a71954.html',
        'http://my.hupu.com/3616496/photo/a1820605.html',
        'http://my.hupu.com/3616496/photo/a1820606.html',
        'http://my.hupu.com/3616496/photo/a1820672.html',
        'http://my.hupu.com/3616496/photo/a1820673.html',
        'http://my.hupu.com/3616496/photo/a1820741.html',
        'http://my.hupu.com/3616496/photo/a1820742.html',
        'http://my.hupu.com/3616496/photo/a1766130.html',
        'http://my.hupu.com/3616496/photo/a1806265.html'
    ]
    albums = selectUrls(album_urls, offset, row_count)
    albums = sorted(albums, key = lambda a: album_urls.index(a.get('url')) )
    pagenums = int( ceil( len(album_urls)/row_count ))
    nav = pagination(currentpage, pagenums, 2)
    return render_template('page.html', albums=albums, nav=nav, currentpage=currentpage+1, Banner=u'灌篮高手', func=sys._getframe().f_code.co_name)

@app.route('/MM/')
def mm():
    currentpage, offset, row_count = selectLIMIT(request)
    album_urls = [
        'http://my.hupu.com/16355386/photo/a211504.html',
        'http://my.hupu.com/sunyatsen/photo/a135716.html',
        'http://my.hupu.com/MasamiSaiko/photo/a1815728.html',
        'http://my.hupu.com/MasamiSaiko/photo/a1807616.html'
    ]
    albums = selectUrls(album_urls, offset, row_count)
    pagenums = int( ceil( len(album_urls)/row_count ))
    nav = pagination(currentpage, pagenums, 2)
    return render_template('page.html', albums=albums, nav=nav, currentpage=currentpage+1, Banner=u'姑娘', func=sys._getframe().f_code.co_name)

@app.route('/MJ/')
def mj():
    currentpage, offset, row_count = selectLIMIT(request)
    album_urls = [
        'http://my.hupu.com/329273/photo/a1777785.html',
        'http://my.hupu.com/14556892/photo/a1788576.html',
        'http://my.hupu.com/hoopchinalv/photo/a65885.html',
        'http://my.hupu.com/16746798/photo/a1808304.html',
        'http://my.hupu.com/healmyself24/photo/a107614.html',
        'http://my.hupu.com/3862090/photo/a131620.html'
    ]
    albums = selectUrls(album_urls, offset, row_count)
    pagenums = int( ceil( len(album_urls)/row_count ))
    nav = pagination(currentpage, pagenums, 2)
    return render_template('page.html', albums=albums, nav=nav, currentpage=currentpage+1, Banner='Michael Jordan', func=sys._getframe().f_code.co_name)


@app.route('/preview/')
def preview():
    url = request.args.get('url')
    try:
        page = abs(int(request.args.get('p')))
    except TypeError as e:
        page = 0
    print 'page',page
    if url:
        g.cur.execute(''' SELECT `picsUrls`,`title`,`pics` FROM `albums` WHERE `url` = %s''',(url,))
        r = g.cur.fetchone()
        if r:
            count = r.get('pics')
            thumbnails = re.sub( 'big.', 'small.', r.get('picsUrls')).split('\n')#[0:20]
            return render_template('preview.html',
                    title = r.get('title'),
                    imgs = thumbnails,
                    url = url,
                    count = count
                )
        else:
            return 'don\'t found!'
    else:
        return abort(400)

@app.route('/donate/')
def donate():
    return render_template('donate.html')

# @app.route('/debug')
# def debug():
#     raise KeyError
#     return render_template('donate.html')