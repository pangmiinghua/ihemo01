# coding:utf-8
from iHome.models import Area
from iHome.utils.response_code import RET
from . import api
from iHome.utils.common import login_required
from flask import current_app,jsonify

@api.route('/areas',methods=["GET"])
def get_areas():
    """提供城区信息
    1.直接查询所有城区信息
    2.构造城区信息响应数据
    3.响应城区信息
    """
    try:
        areas = Area.query.all()  #获取所有城区信息
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询地区数据失败')
    area_dict_list = []
    for area in areas:
        area_dict_list.append(area.to_dict())
    return jsonify(errno=RET.OK,errmsg='OK',data=area_dict_list)

