import datetime
import logging
import time

from flask import abort, jsonify
from flask import render_template, g, request, session, url_for, redirect
from info import constants, db
from info import response_code
from info.models import User, News
from info.utils.comment import user_login_data
from . import admin_blue


@admin_blue.route('/news_edit_detail')
def news_edit_detail():
    return render_template('admin/news_edit_detail.html')


@admin_blue.route('/news_edit')
def news_edit():
    page = request.args.get('p', 1)
    try:
        page = int(page)
    except Exception as e:
        logging.error(e)
        page = 1
    current_page = 1
    total_page = 1
    news_list = []
    try:
        paginate = News.query.filter(News.status == 0).order_by(News.create_time.desc()).paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
        current_page = paginate.page
        total_page = paginate.pages
        news_list = paginate.items
    except Exception as e:
        logging.error(e)
        abort(404)
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())
    context = {
        'current_page': current_page,
        'total_page': total_page,
        'news_list': news_dict_list
    }


    return render_template('admin/news_edit.html', context=context)


@admin_blue.route('/news_review_action', methods=['post'])
def news_review_action():
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    if not all([news_id, action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数不全')
    if action not in ['accept', 'reject']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    try:
        news = News.query.get(news_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻失败')
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg='新闻不存在')
    if action == 'accept':
        news.status = 0
    else:
        reason = request.json.get('reason')
        if not reason:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数不全')
        news.status = -1
    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='同步数据库失败')
    return jsonify(errno=response_code.RET.OK, errmsg='OK')



@admin_blue.route('/news_review_detail/<int:news_id>')
def news_review_detail(news_id):
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        logging.error(e)
        abort(404)
    if not news:
        abort(404)
    context = {
        'news': news.to_dict()
    }
    return render_template('admin/news_review_detail.html', context=context)


@admin_blue.route('/news_review')
def news_review():
    page = request.args.get('p', 1)
    keyword = request.args.get('keyword')
    try:
        page = int(page)
    except Exception as e:
        logging.error(e)
        page = 1
    news_list = []
    current_page = 1
    total_page = 1
    try:
        if keyword:
            paginate = News.query.filter(News.status != 0, News.title.contains(keyword)).order_by(
                News.create_time.desc()).paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
        else:
            paginate = News.query.filter(News.status != 0).order_by(News.create_time.desc()).paginate(page,
                                                                                                      constants.ADMIN_NEWS_PAGE_MAX_COUNT,
                                                                                                      False)
        current_page = paginate.page
        total_page = paginate.pages
        news_list = paginate.items
    except Exception as e:
        logging.error(e)
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())
    context = {
        'current_page': current_page,
        'total_page': total_page,
        'news_list': news_dict_list
    }

    return render_template('admin/news_review.html', context=context)


@admin_blue.route('/user_list')
def user_list():
    page = request.args.get('p', 1)
    try:
        page = int(page)
    except Exception as e:
        logging.error(e)
        page = 1
    users = []
    total_page = 1
    current_page = 1
    try:
        paginate = User.query.filter(User.is_admin == 0).paginate(page, constants.ADMIN_USER_PAGE_MAX_COUNT, False)
        users = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        logging.error(e)
    user_dict_list = []
    for user in users:
        user_dict_list.append(user.to_admin_dict())
    context = {
        'users': user_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }
    return render_template('admin/user_list.html', context=context)


@admin_blue.route('/user_count')
def user_count():
    # 用户总人数
    total_count = 0
    month_count = 0
    day_count = 0
    try:
        total_count = User.query.filter(User.is_admin != 1).count()
    except Exception as e:
        logging.error(e)
    # 月新增
    t = time.localtime()
    month_begin_str = "%d-%02d-1" % (t.tm_year, t.tm_mon)
    month_begin_date = datetime.datetime.strptime(month_begin_str, "%Y-%m-%d")
    try:
        month_count = User.query.filter(User.create_time >= month_begin_date, User.is_admin == 0).count()
    except Exception as e:
        logging.error(e)
    # 日新增
    t = time.localtime()
    day_begin_str = "%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)
    day_begin_date = datetime.datetime.strptime(day_begin_str, "%Y-%m-%d")
    try:
        day_count = User.query.filter(User.is_admin == 0, User.create_time >= day_begin_date).count()
    except Exception as e:
        logging.error(e)
    today_begin = "%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)
    today_begin_date = datetime.datetime.strptime(today_begin, "%Y-%m-%d")
    # 日活
    active_date = []
    active_count = []
    for i in range(15):
        # 计算一天开始
        begin_date = today_begin_date - datetime.timedelta(days=i)
        # 计算一天结束
        end_date = today_begin_date - datetime.timedelta(days=(i - 1))

        # 查询每一天的日活跃量
        count = User.query.filter(User.is_admin == 0, User.last_login >= begin_date,
                                  User.last_login < end_date).count()

        active_count.append(count)
        # 需要将datetime类型的begin_date，转成时间字符串，因为前段的折线图框架需要的是字符串
        active_date.append(datetime.datetime.strftime(begin_date, '%Y-%m-%d'))

    # 为了保证今天在X轴的最左侧，需要反转列表
    active_date.reverse()
    active_count.reverse()
    context = {
        'total_count': total_count,
        'month_count': month_count,
        'day_count': day_count,
        'active_count': active_count,
        'active_date': active_date
    }
    return render_template('admin/user_count.html', context=context)


@admin_blue.route('/')
@user_login_data
def admin_index():
    user = g.user
    if not user:
        return redirect(url_for('admin.admin_login'))
    context = {
        'user': user.to_dict()
    }
    return render_template('admin/index.html', context=context)


@admin_blue.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        is_admin = session.get('is_admin', False)
        user_id = session.get('user_id', None)
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))

        return render_template('admin/login.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not all([username, password]):
            return render_template('admin/login.html', errmsg='缺少参数')
        try:
            user = User.query.filter(User.nick_name == username).first()
        except Exception as e:
            logging.error(e)
            return render_template('admin/login.html', errmsg='查询用户失败')
        if not user:
            return render_template('admin/login.html', errmsg='用户不存在')
        if not user.check_password(password):
            return render_template('admin/login.html', errmsg='用户名或密码错误')
        session['user_id'] = user.id
        session['mobile'] = user.mobile
        session['nick_name'] = user.nick_name
        session['is_admin'] = user.is_admin
        return redirect(url_for('admin.admin_index'))
