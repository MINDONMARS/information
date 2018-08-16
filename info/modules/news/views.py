import logging
from flask import abort, g, render_template
from info import constants, db
from info.models import News
from . import news_blue
from info.utils.comment import user_login_data


@news_blue.route('/detail/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    :param news_id: 新闻id
    :return: 新闻详情
    """
    # 查from info.utils.comment import get_user_info询用户基本信息
    #
    # user = get_user_info()
    user = g.user
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
    # 判断用户是否收藏过该新闻
    is_collected = False
    if news in user.collection_news:
        is_collected = True
    # 构造渲染详情页上下文
    context = {
        'user': user.to_dict() if user else None,
        'news_clicks': news_clicks,
        'news': news,
        'is_collected': is_collected
    }
    return render_template('news/detail.html', context=context)
