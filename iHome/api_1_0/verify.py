#coding:utf-8
# 图片验证和短信验证
import random
import re

from flask import current_app
from flask import json
from flask import session

from iHome.models import User
from iHome.utils.sms import CCP
from .import api
from flask import abort, jsonify
from flask import make_response
from flask import request
from iHome import redis_store,constants
from iHome.utils.captcha.captcha import captcha
from iHome.utils.response_code import RET
import logging


@api.route("/sms_code",methods=["POST"])
def send_sms_code():
    """发送短信验证码
   1.获取参数:手机号，验证码，uuid
   2.判断是否缺少参数，并对手机号格式进行校验
   3.获取服务器存储的验证码
   4.跟客户端传入的验证码进行对比
   5.如果对比成功就生成短信验证码
   6.调用单例类发送短信
   7.如果发送短信成功，就保存短信验证码到redis数据库
   8.响应发送短信的结果
   """
    json_str = request.data
    json_dict = json.loads(json_str)
    mobile = json_dict.get('mobile')
    imageCode_client = json_dict.get('imageCode')
    uuid = json_dict.get('uuid')

    if not all([mobile,imageCode_client,uuid]):
        return jsonify(errno=RET.PARAMERR,errmsg="缺少参数")

    if not re.match(r'^1[345678][0-9]{9}$',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号码格式错误')
    #   获取服务器储存的验证码
    try:
        imageCode_server = redis_store.get('ImageCode:%s'% uuid)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询验证码失败')
    if not imageCode_server:
        return jsonify(errno=RET.NODATA,errmsg='验证码不存在')
    # 验证码对比
    # lower()转换大小写，都转小写
    if imageCode_server.lower() != imageCode_client.lower():
        return jsonify(errno=RET.PARAMERR,errmsg='验证码输入有误')
    #成功就生成短线验证码  random生成随机数的函数方法
    sms_code = '%06d'%random.randint(0,999999)
    current_app.logger.debug(sms_code)

    # 6.调用单例类发送短信
    result = CCP().send_sms_code(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES/60], '1')
    if result != 1:
        return jsonify(errno=RET.THIRDERR, errmsg='发送短信验证码失败')


    # 发短线成功，就保存短信验证码到redis数据库
    try:
        redis_store.set('SMS:%s'%mobile,sms_code,constants
                        .SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='储存短信验证码失败')

    return jsonify(errno=RET.OK,errmsg='发送短信验证码成功')

# 定义变量记录上一次uuid
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
    # current_app.logger.debug('app验证码内容为：' + text)

    # 3、使用redis数据库缓存图片验证码，uuid作为key
    try:
        if last_uuid:
            redis_store.delete('ImageCode:%s'% last_uuid)

        redis_store.set('ImageCode:%s'% uuid,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e :
        # print e
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='保存验证码失败')

    global last_uuid
    last_uuid = uuid

    # 4.响应图片验证码
    # 修改响应头信息，指定响应的内容是image/jpg
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'    #相应是记得要转img图片格式，不然默认是html
    # 响应图片验证码
    return response

