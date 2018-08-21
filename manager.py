from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db, models
from info.models import User

app = create_app('dev')
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.option('-u', '-username', dest='username')
@manager.option('-p', '-password', dest='password')
@manager.option('-m', '-mobile', dest='mobile')
def createsuperuser(username, password, mobile):
    """
     创建管理员的函数
     :param name: 管理员名字
     :param password: 管理员密码
    """
    if not all([username, password, mobile]):
        print('缺少参数')
    else:
        user = User()
        user.nick_name = username
        user.password = password
        user.mobile = mobile
        user.is_admin = True
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)


if __name__ == '__main__':
    manager.run()
