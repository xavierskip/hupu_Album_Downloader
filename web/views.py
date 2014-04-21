#-*- coding:utf-8 -*-
from flask import g,request,jsonify
from flask import render_template,redirect,url_for
from web import app
from db import Database
from db import store_img
import base64
from hupu import HupuAlbum
from hupu import detect_album_path
import time

def img_base64(img,ext):
    return 'data:image/%s;base64,%s' %(ext,base64.b64encode(img))

#Database
def connect_db():
    return Database(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g,'db'):
        g.db.close()

#Route
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/url',methods=['POST'])
def url():
    url = request.form['url']
    page = detect_album_path(url)
    if page:
        start = time.time()
        album = HupuAlbum(url)
        album.save()
        spend = time.time() - start
        # save info
        imgBase64=''
        if album.stat==200:
            # store cover
            cover = album.session.get(album.cover).content
            ext = album.cover.split('.')[-1]
            cover_id = store_img(app.config['COVERS'],cover,ext)
            imgBase64 = img_base64(cover,ext)
            # store the data
            g.db.update(album.url,album.title,cover_id,album.pics,album.get_pics,album.pics_urls)
        return jsonify(
            stat = album.stat,
            homepage = album.url,
            title = album.title,
            cover = album.cover,
            pics = album.pics,
            get_pics = album.get_pics,
            pics_urls = album.pics_urls,
            imgBase64 = imgBase64,
            time = spend
        )
    else:
        return jsonify(stat = 2)

@app.route('/albums')
def albums():
    cur = g.db.cur
    cur.execute('SELECT Homepage,Title,Cover,HasPics,GetPics,Times FROM albums order by LogTime desc')
    albums = [dict(homepage=row[0],title=row[1],cover=row[2],hasPics=row[3],getPics=row[4],times=row[5]) for row in cur.fetchall()]
    return render_template('albums.html',albums=albums)

@app.route('/<path:img>')
def cover_img(img):
    return redirect(url_for('static',filename=img))
