from flask import Flask

app = Flask(__name__)
app.config.from_object('config')
app.config.from_pyfile('web.cfg', silent=True)

from . import views