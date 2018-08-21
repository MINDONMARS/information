import logging
from flask import g
from flask import render_template, current_app, jsonify
from flask import request
from info.utils.comment import user_login_data
from info import constants
from info import response_code
from info.models import News, Category
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
    # 1
    cid = request.args.get('cid', '1')
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')
    # 2
    if not all([cid, page, per_page]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    # 3
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    # 4. 根据参数分页查询
    try:
        if cid == 1:
            # 最新分类, 查询所有新闻按时间倒序排序
            paginate = News.query.filter(News.status == 0).order_by(News.create_time.desc()).paginate(page, per_page, False)
        else:
            paginate = News.query.filter(News.category_id == cid, News.status == 0).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询数据失败')
    # 生成响应数据
    total_page = paginate.pages  # 总页数
    current_page = paginate.page  # 当前页
    news_list = paginate.items  # 当前页的数据列表
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())
    # 返回响应数据
    return jsonify(errno=response_code.RET.OK, errmsg='OK', cid=cid, current_page=current_page, total_page=total_page,
                   news_dict_list=news_dict_list)


@index_blue.route('/')
@user_login_data
def index():
    """
    添加点击排行(右侧1-6)
    """
    # 改用装饰器
    # 从session查询user_id
    # from info.utils.comment import get_user_info
    # user = get_user_info()
    user = g.user
    # 点击排行
    news_clicks = None
    categories = None
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
        # 新闻分类
        categories = Category.query.all()
    except Exception as e:
        logging.error(e)
    # 构造渲染模板的上下文
    context = {
        'user': user.to_dict() if user else None,
        'news_clicks': news_clicks,
        'categories': categories
    }

    return render_template('news/index.html', context=context, categories=categories)


@index_blue.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
