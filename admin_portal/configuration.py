import os
from flask import Flask, Blueprint
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://{}:{}@{}/{}".format("root",
                                                                     "RmitUniversityPiot",
                                                                     "35.197.173.168",
                                                                     "SmartLibrary")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy()

basedir = os.path.abspath(os.path.dirname(__file__))

api = Blueprint("api", __name__)
site = Blueprint("site", __name__)

db.init_app(app)
app.register_blueprint(api)
app.register_blueprint(site)

ma = Marshmallow(app)
