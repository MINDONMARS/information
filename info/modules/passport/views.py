import logging
import re, random

from flask import abort, jsonify
from flask import make_response
from flask import request
from info import constants
from info import redis_store
from info import response_code
from info.libs.yuntongxun.sms import CCP
# from utils.captcha.captcha import captcha
from . import passport_blue


@passport_blue.route('/sms_code', methods=['port'])
def send_sms_code():
    """发送短信验证码
    1.接受参数：mobile, image_code, image_code_id
    2.校验参数：判断参数是否齐全，判断手机号格式是否正确
    3.使用image_code_id从redis中读取出服务器存储的图片验证码
    4.使用用户输入的图片验证码 对比 服务器存储的图片验证码
    5.如果对比成功生成短信验证码，长度是6位的随机数字
    6.再使用CCP()单例发送短信验证码
    7.发送短信验证码成功，就把短信验证码存储到redis()
    8.返回短信验证码发送的结果
    """
    # 接收参数: mobile, image_code, image_code_id
    json_dict = request.json
    mobile = json_dict.get('mobile')
    image_code_client = json_dict.get('image_code')
    image_code_id = json_dict.get('image_code')
    # 校验参数: 是否齐全, 手机号格式是否正确
    if not all([mobile, image_code_client, image_code_id]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少必传参数')
    if not re.match('^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号格式错误')
    # 使用image_code_id从redis中读取出服务器存储的图片验证码
    try:
        image_code_server = redis_store.get(
            'imageCode:' + image_code_id
        )
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='查询验证码失败')
    # 判断image_code_id 是否存在
    if not image_code_server:
        return jsonify(errno=response_code.RET.NODATA, errmsg='图片验证码不存在')
    # 4.使用用户输入的验证码对比服务器存储的验证码
    if image_code_client.lower() != image_code_server.lower():
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='验证码输入有误')
    # 成功 : 生成6位验证码
    sms_code = "%06d" % random.randint(0, 999999)
    logging.debug(sms_code)
    # CCP()单例发送验证码
    result = CCP().send_sms_code(mobile, [sms_code, 5], 1)
    if result != 0:
        return jsonify(errno=response_code.RET.THIRDERR, errmsg='发送短信失败')
    # 发送成功, 将验证码存储到redis
    try:
        redis_store.set('SMS:', + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DATAERR, errmsg='存储短信失败')

    # 返回结果
    return jsonify(errno=response_code.RET.OK, errmsg='发送短信成功')

#
# @passport_blue.route('/image_code')
# def get_image_code():
#     # 接收图片uuid
#     image_code_id = request.args.get("imageCodeId")
#     # 校验uuid
#     if not image_code_id:
#         abort(400)
#     # 生成验证码的图片和文字信息
#     name, text, image = captcha.instance()
#     # 讲uuid和图片验证码文字绑定到redis
#     try:
#         redis_store.set("imageCode:" + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
#     except Exception as e:
#         logging.error(e)
#         abort(500)
#     # 响应
#     response = make_response()
#     response.header['Content-Type'] = 'image/jpg'
#     return response

