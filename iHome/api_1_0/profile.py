# coding:utf-8
from flask import current_app, jsonify
from flask import session
from iHome.models import User
from iHome.utils.response_code import RET
from . import api



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