import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect, csrf
from redis import StrictRedis

from config import configs

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
    redis_store = StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT, decode_responses=True)
    CSRFProtect(app)
    # 注册蓝图
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)
    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)
    from info.modules.news import news_blue
    app.register_blueprint(news_blue)
    # 导入自定义过滤器
    from info.utils.comment import do_rank
    app.add_template_filter(do_rank, 'rank')
    # 在每一次相应中, 都写入一个cookie 值为csrf_token
    @app.after_request
    def after_request_set_csrf_token(response):
        """
        监听每一次请求之后的请求勾子, 给每一次响应中都写入一个cookie, 值为csrf_token
        """
        # 生成csrf_toke
        #  generate_csrf()生成一个签名后的csrf_token并写入session
        csfr_token = csrf.generate_csrf()
        # 将csrf_token写入cookie
        response.set_cookie('csrf_toke', csfr_token)
        return response

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

