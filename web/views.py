#-*- coding:utf-8 -*-
from flask import g,request,jsonify
from flask import render_template,redirect,url_for
from hupu import HupuAlbum
from hupu import get_content
from web import app
from db import Database
from db import store_img
import base64

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
    album = HupuAlbum.Album(url)
    album.save()
    #
    imgBase64=''
    if album.stat==1:
        # store cover
        cover = get_content(album.cover)
        ext = album.cover.split('.')[-1]
        cover_id = store_img(app.config['COVERS'],cover,ext)
        imgBase64 = img_base64(cover,ext)
        # store the data
        g.db.update(album.homepage,album.title,cover_id,album.hasPics,album.getPics,album.imgUrls)

    return jsonify(
        stats = album.stat,
        homepage = album.homepage,
        title = album.title,
        cover = album.cover,
        hasPics = album.hasPics,
        getPics = album.getPics,
        imgUrls = album.imgUrls,
        imgBase64 = imgBase64
    )

@app.route('/albums')
def albums():
    cur = g.db.cur
    cur.execute('SELECT Homepage,Title,Cover,HasPics,GetPics,Times FROM albums order by LogTime desc')
    albums = [dict(homepage=row[0],title=row[1],cover=row[2],hasPics=row[3],getPics=row[4],times=row[5]) for row in cur.fetchall()]
    return render_template('albums.html',albums=albums)

@app.route('/<path:img>')
def cover_img(img):
    return redirect(url_for('static',filename=img))
