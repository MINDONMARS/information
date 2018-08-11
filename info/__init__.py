from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from config import configs

db = SQLAlchemy()
redis_store = None  # type: StrictRedis


def create_app(config_name):

    config_class = configs[config_name]
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    Session(app)
    global redis_store
    redis_store = StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)
    CSRFProtect(app)
    return app
