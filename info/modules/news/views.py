from flask import abort, g, render_template, request, jsonify
from info import constants, db, response_code
from info.models import News, Comment, CommentLike, User
from . import news_blue
from info.utils.comment import user_login_data
import logging


@news_blue.route('/followed_user', methods=['POST'])
@user_login_data
def followed_user():
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')
    user_id = request.json.get('user_id')
    action = request.json.get('action')
    if not all([user_id, action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数不全')
    if action not in ['follow', 'unfollow']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    try:
        author = User.query.get(user_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询数据失败')
    if not author:
        return jsonify(errno=response_code.RET.NODATA, errmsg='用户不存在')
    if action == 'follow':
        if author not in user.followed:
            user.followed.append(author)
    else:
        if author in user.followed:
            user.followed.remove(author)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='操作失败')
    return jsonify(errno=response_code.RET.OK, errmsg='OK')



@news_blue.route('/comment_like', methods=['POST'])
@user_login_data
def comment_like():
    """
    1.用户是否登录
    2.comment_id, action
    3.校验参数是否齐全, action是否在范围内(add/remove)
    4.查询被点赞的数据是否存在
    5.根据action的值实现点赞/取消点赞
    6.数据同步到数据库.
    7.返回点赞/取消点赞结果
    """
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')
    json_dict = request.json
    comment_id = json_dict.get('comment_id')
    action = json_dict.get('action')
    if not all([comment_id, action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少必传参数')
    if action not in ['add', 'remove']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少必传参数')
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询失败')
    if not comment:
        return jsonify(errno=response_code.RET.NODATA, errmsg='评论不存在')
    comment_like_model = CommentLike.query.filter(CommentLike.user_id == user.id, CommentLike.comment_id == comment.id).first()
    if action == 'add':
        if not comment_like_model:
            comment_like_model = CommentLike()
            comment_like_model.user_id = user.id
            comment_like_model.comment_id = comment.id
            # 点赞数 + 1
            comment.like_count += 1
            db.session.add(comment_like_model)
    else:
        if comment_like_model:
            comment.like_count -= 1
            db.session.delete(comment_like_model)
    # 提交数据库
    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='操作失败')
    return jsonify(errno=response_code.RET.OK, errmsg='操作成功')


@news_blue.route('/news_comment',  methods=['POST'])
@user_login_data
def news_comment():
    """
    1.判断用户是否登录
    2.接收参数, news_id, comment, parent_id
    3.校验参数: 是否齐全, news_id, parent_id是否为整数
    4.判断新闻是否存在, 存在才可以评论
    5.根据参数创建Comment模型对象, 给属性赋值
    6.同步到数据库,
    7.响应前端, 评论内容也发过去显示在前端页面
    """
    user = g.user
    # 接收参数
    json_dict = request.json
    news_id = json_dict.get('news_id')
    comment_content = json_dict.get('comment')
    parent_id = json_dict.get('parent_id')
    # 校验参数
    if not all([news_id, comment_content]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少必传参数')
    # 是否为整数
    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    # 数据库是否有该新闻
    try:
        news = News.query.get(news_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询数据失败')
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg='新闻不存在')
    # 创建comment对象
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news.id
    comment.content = comment_content
    if parent_id:
        comment.parent_id = parent_id
    # 同步数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='评论失败')
    return jsonify(errno=response_code.RET.OK, errmsg='评论成功', data=comment.to_dict())




@news_blue.route('/news_collect', methods=['post'])
@user_login_data
def news_collect():
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')
    # 接收参数
    json_dict = request.json
    news_id = json_dict.get('news_id')
    action = json_dict.get('action')
    # 校验参数
    if not all([news_id, action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少必传参数')
    if action not in ['collect', 'cancel_collect']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    # 查询新闻数据
    try:
        news = News.query.get(news_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询失败')
    # 如果没有新闻
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg='数据不存在')
    # 根据action的值实现收藏/取消收藏
    #  收藏

    if action == 'collect':
        if news not in user.collection_news:
            user.collection_news.append(news)
    # 取消收藏
    else:
        if news in user.collection_news:
            user.collection_news.remove(news)
    # 提交数据到数据库
    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg="操作失败")
    # 操作成功响应
    return jsonify(errno=response_code.RET.OK, errmsg="操作成功")



@news_blue.route('/detail/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    :param news_id: 新闻id
    :return: 新闻详情
    """
    # 查from info.utils.comment import get_user_info询用户基本信息

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
    if user:
        if news in user.collection_news:
            is_collected = True
    comments = None
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        logging.error(e)
    # comment_dict_list = []
    # for comment in comments:
    #     comment_dict_list.append(comment.to_dict())
    # 判断当前用户为哪些评论点了赞
    comment_like_ids = []
    if user:
        try:
            # 拿到当前用户模型对象 点赞的所有 评论的模型对象
            comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id).all()
            # 把 这些评论的id放到列表里
            comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            logging.error(e)
    # 准备渲染的数据
    comment_dict_list = []
    for comment in comments:
        comment_dict = comment.to_dict()
        # 给字典加个键值对
        comment_dict['is_like'] = False
        # 如果评论的id在用户点赞的列表里
        if comment.id in comment_like_ids:
            comment_dict['is_like'] = True
        comment_dict_list.append(comment_dict)
    is_followed = False
    if user and news.user:
        if news.user in user.followed:
            is_followed = True
    # 构造渲染详情页上下文
    context = {
        'user': user.to_dict() if user else None,
        'news_clicks': news_clicks,
        'news': news.to_dict(),
        'is_collected': is_collected,
        'comments': comment_dict_list,
        'is_followed': is_followed
    }
    return render_template('news/detail.html', context=context)
