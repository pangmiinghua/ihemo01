# coding:utf-8
from flask import current_app, jsonify
from flask import request
from flask import session

from iHome import constants
from iHome import db
from iHome.models import User
from iHome.utils.image_storage import upload_image
from iHome.utils.response_code import RET
from . import api

@api.route("/users/avatar",methods=["POST"])
def ind():
    try:
        image_data = request.files.get('avatar')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="图片获取失败")

    try:
        key = upload_image(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="上传图片失败")

    user_id = session.get('user_id')
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户失败")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户不存在')

    user.avatar_url = key

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="储存用户头像失败")

    avatar_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg="上传头像成功",data=avatar_url)

@api.route("/users",methods=["GET"])
def get_user_info():
    user_id = session.get('user_id')

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户数据为空')

    response_info_dict  = user.to_dict()

    return jsonify(errno=RET.OK,errmsg="OK",data = response_info_dict)