import logging
from flask import render_template, session
from info import constants
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
    # 构造渲染详情页上下文
    context = {
        'user': user.to_dict() if user else None,
        'news_clicks': news_clicks
    }
    return render_template('news/detail.html', context=context)
