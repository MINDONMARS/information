import logging

from flask import abort
from flask import render_template, session
from info import constants, db
from info.models import User, News
from . import news_blue


@news_blue.route('/detail/<int:news_id>')
def news_detail(news_id):
    """
    :param news_id: 新闻id
    :return: 新闻详情
    """
    # 查询用户基本信息
    user_id = session.get('user_id', None)
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            logging.error(e)
    # 查询点击排行信息
    news_clicks = None
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        logging.error(e)
    # 查询新闻详情
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        logging.error(e)
    if not news:
        # 抛出404 对404 统一处理
        abort(404)
    # 重置新闻点击量
    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()

    # 构造渲染详情页上下文
    context = {
        'user': user.to_dict() if user else None,
        'news_clicks': news_clicks,
        'news': news
    }
    return render_template('news/detail.html', context=context)
