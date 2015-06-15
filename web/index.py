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
            return render_template('logon.html',user=user,lastDate=LASTDATE)
    else:
        return render_template('index.html',lastDate=LASTDATE)

@app.route('/getalbum',methods=['POST'])
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
            try:
                user = request.form['user']
                pwd = request.form['password']
            except KeyError, e:
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
        cover = album.session.get(album.cover).content
        ext = album.cover.split('.')[-1]
        coverimg = img_base64(cover,ext)
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

@app.route('/albums')
def albums():
    imgs = 60.0# how much img in one page , float num
    try:
        currentpage = abs(int(request.args.get('page')))
    except Exception, e:
        currentpage = 1
    imgstart,imgend = ( int((currentpage-1)*imgs),int(imgs))
    g.cur.execute('''SELECT count(*) from `albums`''')
    imgcount = int(g.cur.fetchone().get('count(*)'))
    pagenums = int(ceil(imgcount/imgs))
    # get albums info
    g.cur.execute(''' SELECT url,title,cover,pics,getPics,times FROM albums order by logTime desc LIMIT %s,%s''',(imgstart,imgend))
    albums = [dict(url=row.get('url'),title=row.get('title'),cover=row.get('cover'),pics=row.get('pics'),getPics=row.get('getPics'),times=row.get('times')) \
                for row in g.cur.fetchall() ]
    # pages = dict(current=page,number=pn)
    step = 2
    rangeStart, rangeEnd = currentpage-step,currentpage+step
    if rangeStart < 1 and rangeEnd > pagenums:
        pages = [ i for i in range(1,pagenums+1)]
    elif rangeStart <= 1+1:
        pages = [ i for i in range(1,rangeEnd+1)]
        pages.extend(['',pagenums])
    elif rangeEnd >= pagenums-1:
        pages = [1,'']
        pages.extend([ i for i in range(rangeStart,pagenums+1)])
    else:
        pages = [1,'']
        pages.extend([i for i in range(rangeStart,rangeEnd+1)])
        pages.extend(['',pagenums])

    return render_template('albums.html',albums=albums,pages=pages,currentpage=currentpage)
    # return "<h1>UNDER CONSTRUCTION!</h1>"

@app.route('/album')
def album():
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

@app.route('/zip')
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

@app.route('/donate')
def donate():
    return render_template('donate.html')

# @app.route('/debug')
# def debug():
#     raise KeyError
#     return render_template('donate.html')