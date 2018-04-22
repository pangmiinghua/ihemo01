# coding:utf-8
# 个人中心
from flask import current_app, jsonify
from flask import g
from flask import request
from flask import session

from iHome import constants
from iHome import db
from iHome.models import User
from iHome.utils.image_storage import upload_image
from iHome.utils.response_code import RET
from . import api
from iHome.utils.common import login_required

# 实名认证
@api.route("/users/auth",methods=["POST"])
@login_required
def set_user_auth():
    """"
    实名认证
    0.判断用户是否登录
    1.获取实名认证参数：real_name,id_card,并判断是否为空
    2.查询当前的登录用户user模型
    3.将real_name,id_card赋值给user模型
    4.保存到数据库
    5.响应实名认证结果
    """
    json_dict = request.json
    real_name = json_dict.get('real_name')
    id_card = json_dict.get('id_card')
    if not ([real_name,id_card]):
        return jsonify(errno=RET.PARAMERR,errmsg='缺少参数')
    # 在common文件自定义路由器进行判断是否登录时用g变量记录了当
    # 用户登录时的user_id
    user_id = g.user_id
    try:  #因为可能会获取出错，所以用try：
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询用户失败")
    if not user:
        return jsonify(errno=RET.NODATA,errmsg="用户不存在")

    user.real_name = real_name
    user.id_card = id_card

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()  #事务回滚
        return jsonify(errno=RET.DBERR,errmsg="保存数据失败")

    return jsonify(errno=RET.OK,errmsg="认证成功")


# 修改用户名
@api.route("/users/name",methods=["PUT"])
@login_required
def set_user_name():
    json_dict = request.json
    new_name = json_dict.get('name')
    if not new_name:
        return jsonify(errno=RET.DATAERR,errmsg="缺少参数")
    user_id = session.get('user_id')
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询用户数据失败")
    if not user:
        return jsonify(errno=RET.NODATA,errmsg="用户不存在")

    user.name = new_name
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="保存用户数据失败")

    return jsonify(errno=RET.OK,errmsg="修改用户名成功")

# 上传图片
@api.route("/users/avatar",methods=["POST"])
@login_required
def upload_avatar():
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

# 提供以用户信息
@api.route("/users",methods=["GET"])
@login_required
def get_user_info():
    user_id = session.get('user_id')

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户数据为空')

    response_info_dict = user.to_dict()

    return jsonify(errno=RET.OK,errmsg="OK",data = response_info_dict)