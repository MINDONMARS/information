import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from config import configs
from info.modules.index import index_blue

db = SQLAlchemy()
redis_store = None  # type: StrictRedis


def create_app(config_name):

    config_class = configs[config_name]

    # 调用日志的配置方法
    setup_log(config_class.LOGGING_LEVEL)

    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    Session(app)
    global redis_store
    redis_store = StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)
    CSRFProtect(app)
    # 注册蓝图
    app.register_blueprint(index_blue)
    return app


def setup_log(level):
    """
    配置日志等级
    :param level: 日志等级：根据开发环境而变（dev--DEBUG; prod--WARNING）
    :return: None
    """
    # 设置日志的记录等级。
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

