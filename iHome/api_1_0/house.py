# coding:utf-8
from flask import g
from flask import request

from iHome import db
from iHome.models import Area, House
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



@api.route('/houses',methods=['POST'])
@login_required
def pub_house():
    """"发布房源信息
    0、判断是否有登录
    1、获取请求参数
    2、判断参数合法性
    3、创建新模型类，并赋值
    4、提交数据库
    5、返回结果
    """
    json_dict = request.json
    title = json_dict.get('title')
    price = json_dict.get('price')
    address = json_dict.get('address')
    area_id = json_dict.get('area_id')
    room_count = json_dict.get('room_count')
    acreage = json_dict.get('acreage')
    unit = json_dict.get('unit')
    capacity = json_dict.get('capacity')
    beds = json_dict.get('beds')
    deposit = json_dict.get('deposit')
    min_days = json_dict.get('min_days')
    max_days = json_dict.get('max_days')
    facility = json_dict.get('facility')  # [2,4,6,8,10]

    if not all([title, price, address, area_id, room_count,
                acreage, unit, capacity, beds, deposit, min_days, max_days, facility]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数缺失')

    try:  #检验价格
        price = int(float(price)*100)
        deposit = int(float(deposit)*100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='金额格式错误')

    # 3.创建房屋模型对象，并赋值
    house = House()
    house.user_id = g.user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存新房屋数据失败')

    return jsonify(errno=RET.OK, errmsg='发布新房源成功',
                   data={'house_id':house.id})

