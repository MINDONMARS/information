import logging
from flask import render_template, current_app
from flask import session

from info import constants
from info.models import User, News, Category
from . import index_blue


@index_blue.route('/news_list')
def index_news_list():
    """
    1. 接收参数: 当前页, 每页条数, 当前分类id
    2. 校验参数是否齐全
    3. 校验参数是否为整数
    4. 根据参数分页查询
    5. 生成响应
    6. 返回响应
    """



@index_blue.route('/')
def index():
    """
    添加点击排行(右侧1-6)
    """
    # 从session查询user_id
    user_id = session.get('user_id', None)
    # 用user_id在数据库中查询user对象
    user = None

    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            logging.error(e)

    # 点击排行
    news_clicks = None
    categorys = None
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
        # 新闻分类
        categorys = Category.query.all()
    except Exception as e:
        logging.error(e)
    # 构造渲染模板的上下文
    context = {
        'user': user.to_dict() if user else None,
        'news_clicks': news_clicks,
        'categorys': categorys
    }

    return render_template('news/index.html', context=context, categorys=categorys)


@index_blue.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
