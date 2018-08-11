from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db


# app = Flask(__name__)


# class Config(object):
#     DEBUG = True
#     # 配置MySQL:指定数据库位置
#     SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@192.168.103.132:3306/information_09'
#     # 禁用追踪mysql:因为mysql的性能差，如果再去追踪mysql的所有的修改，会再次浪费性能
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#
#     REDIS_HOST = '192.168.73.128'
#     REDIS_PORT = 6379
#
#     SECRET_KEY = 'SECRETKEY'
#
#     SESSION_TYPE = 'redis'
#     SESSION_USE_SIGNER = True
#     SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
#     PERMANENT_SESSION_LIFETIME = 60 * 60 * 24


# app.config.from_object(Config)
# db = SQLAlchemy(app)
# Session(app)
# redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# CSRFProtect(app)
app = create_app('dev')
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/', methods=['GET', 'POST'])
def index():
    return 'index'


if __name__ == '__main__':
    manager.run()
