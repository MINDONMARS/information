import logging
from flask import abort
from flask import make_response
from flask import request
from info import constants
from info import redis_store
from utils.captcha.captcha import captcha
from . import passport_blue


@passport_blue.route('/image_code')
def get_image_code():
    # 接收图片uuid
    image_code_id = request.args.get("imageCodeId")
    # 校验uuid
    if not image_code_id:
        abort(400)
    # 生成验证码的图片和文字信息
    name, text, image = captcha.instance()
    # 讲uuid和图片验证码文字绑定到redis
    try:
        redis_store.set("imageCode:" + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        logging.error(e)
        abort(500)
    # 响应
    response = make_response()
    response.header['Content-Type'] = 'image/jpg'
    return response

