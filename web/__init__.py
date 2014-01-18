from flask import Flask
from web import config
app = Flask(__name__)
app.config.from_object(config)

from web import views
