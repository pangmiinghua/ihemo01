#coding:utf-8
# 图片验证和短信验证
from .import api
from flask import abort, jsonify
from flask import make_response
from flask import request

from iHome import redis_store,constants
from iHome.utils.captcha.captcha import captcha
from iHome.utils.response_code import RET

last_uuid = ""
@api.route('/image_code',methods=['GET'])
def get_image_code():
    """"
    1、获取uuid，并校验uuid
    2、生成图片验证码
    3、使用redis数据库缓存图片验证码，uuid作为key
    4、响应图片验证码
    """

    uuid = request.args.get('uuid')
    if not uuid :
        abort(403)
    #生成图片验证码   text验证码文本信息image验证码图片信息
    name,text,image = captcha.generate_captcha()
    # 3、使用redis数据库缓存图片验证码，uuid作为key
    try:
        if last_uuid:
            redis_store.delete('ImageCode:%s'% last_uuid)

        redis_store.set('ImageCode:%s'% last_uuid,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e :
        print e
        return jsonify(errno=RET.DBERR,errmsg='保存验证码失败')

    global last_uuid
    last_uuid = uuid

    # 4.响应图片验证码
    # 修改响应头信息，指定响应的内容是image/jpg
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'    #相应是记得要转img图片格式，不然默认是html
    # 响应图片验证码
    return response

