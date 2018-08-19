import logging
from flask import render_template, g, redirect, request, url_for, jsonify
from flask import session
from info import constants
from info import response_code, db
from info.models import Category, News
from info.utils.file_storage import upload_file
from . import user_blue
from info.utils.comment import user_login_data


@user_blue.route('/news_list')
@user_login_data
def news_list():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    page = request.args.get('p', 1)
    try:
        page = int(page)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    user_news_list = []
    total_page = 1
    current_page = 1
    try:
        paginate = user.news_list.paginate(page, constants.USER_NEWS_PRE_PAGE, False)
        total_page = paginate.pages
        current_page = paginate.page
        user_news_list = paginate.items
    except Exception as e:
        logging.error(e)

    news_dict_list = []
    for news in user_news_list:
        news_dict_list.append(news.to_basic_dict())
    context = {
        'news_dict_list': news_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }
    return render_template('news/user_news_list.html', context=context)


@user_blue.route('/news_release', methods=['get', 'post'])
@user_login_data
def news_release():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    if request.method == 'GET':
        categories = None
        try:
            categories = Category.query.all()
            categories.pop(0)
        except Exception as e:
            logging.error(e)
        context = {
            "categories": categories
        }
        return render_template('news/user_news_release.html', context=context)
    if request.method == 'POST':
        title = request.form.get('title')  # 新闻标题
        source = '个人发布'
        category_id = request.form.get("category_id")
        digest = request.form.get('digest')
        content = request.form.get('content')
        index_image = request.files.get('index_image')
        if not all([title, source, category_id, digest, content, index_image]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
        try:
            index_image_data = index_image.read()
        except Exception as e:
            logging.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
        try:
            key = upload_file(index_image_data)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=response_code.RET.THIRDERR, errmsg='上传七牛云失败')
        news = News()
        news.title = title
        news.source = source
        news.category_id = category_id
        news.content = content
        news.digest = digest
        news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
        news.user_id = user.id
        news.status = 1
        try:
            db.session.add(news)
            db.session.commit()
        except Exception as e:
            logging.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='添加新闻到数据库失败')
        return jsonify(errno=response_code.RET.OK, errmsg='添加新闻到数据库成功')


@user_blue.route('/user_collection')
@user_login_data
def user_collection():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    page = request.args.get('p', 1)
    try:
        page = int(page)
    except Exception as e:
        logging.error(e)
        page = 1
    news_list = []
    current_page = 1
    total_page = 1
    try:
        paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        logging.error(e)
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())
    context = {
        'news_dict_list': news_dict_list,
        'current_page': current_page,
        'total_page': total_page
    }
    return render_template('news/user_collection.html', context=context)


@user_blue.route('/pass_info', methods=['get', 'post'])
@user_login_data
def pass_info():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')
    if request.method == 'POST':
        # 接收参数
        old_password = request.json.get('old_password')
        new_password = request.json.get('new_password')
        # 校验
        if not all([old_password, new_password]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
        if not user.check_password(old_password):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='旧密码输入错误')
        user.password = new_password
        try:
            db.session.commit()
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DBERR, errmsg='修改密码失败')
        return jsonify(errno=response_code.RET.OK, errmsg='修改密码成功')

    context = {
        'user': user
    }
    return render_template('news/user_pass_info.html', context=context)


@user_blue.route('/pic_info', methods=['get', 'post'])
@user_login_data
def pic_info():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    if request.method == 'GET':
        context = {
            'user': user.to_dict()
        }
        return render_template('news/user_pic_info.html', context=context)
    if request.method == 'POST':
        # 接收参数(文件二进制)
        # 拿到文件对象
        avatar_file = request.files.get('avatar')
        try:
            avatar_data = avatar_file.read()
        except Exception as e:
            logging.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
        try:
            key = upload_file(avatar_data)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=response_code.RET.THIRDERR, errmsg='上传文件到七牛云失败')
        user.avatar_url = key
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='存储头像失败')
        data = {
            'avatar_url': constants.QINIU_DOMIN_PREFIX + key
        }
        return jsonify(errno=response_code.RET.OK, errmsg='存储头像成功', data=data)


@user_blue.route('/base_info', methods=['get', 'post'])
@user_login_data
def base_info():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    if request.method == 'GET':
        context = {
            'user': user.to_dict()
        }
        return render_template('news/user_base_info.html', context=context)
    if request.method == 'POST':
        # 获取参数(nick_name/signature)
        nick_name = request.json.get('nick_name')
        signature = request.json.get('signature')
        gender = request.json.get('gender')
        # 校验
        if not all([nick_name, signature, gender]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
        if gender not in ['MAN', 'WOMAN']:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

        user.nick_name = nick_name
        user.signature = signature
        user.gender = gender
        try:
            db.session.commit()
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DBERR, errmsg='修改失败')
        session['nick_name'] = nick_name
        return jsonify(errno=response_code.RET.OK, errmsg='ok')


@user_blue.route('/info')
@user_login_data
def user_info():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    context = {
        'user': user.to_dict()
    }
    return render_template('news/user.html', context=context)
