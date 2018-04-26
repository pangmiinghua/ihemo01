# coding:utf-8
import datetime

from flask import g
from flask import request, jsonify,current_app

from iHome import db
from iHome.models import House, Order
from iHome.utils.response_code import RET
from . import api
from iHome.utils.common import login_required



@api.route('/orders',methods=["POST"])
@login_required
def create_order():
    """创建、提交订单
        0.判断用户是否登录
        1.获取参数:house_id, start_date, end_date
        2.判断参数是否为空
        3.校验时间格式是否合法
        4.通过house_id，判断要提交的房屋是否存在
        5.判断当前房屋是否已经被预定了
        6.创建订单模型对象，并赋值
        7.将数据保存到数据库
        8.响应提交订单结果
        """

    # 1.获取参数:house_id, start_date, end_date
    json_dict = request.json
    house_id = json_dict.get('house_id')
    start_data_str = json_dict.get('start_data')
    end_data_str = json_dict.get('end_data')

    # 2.判断参数是否为空
    if not all([house_id,start_data_str,end_data_str]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 3.校验时间格式是否合法
    try:
        start_data = datetime.datetime.strptime(start_data_str,'%Y-%m-%d')
        end_data = datetime.datetime.strptime(end_data_str,'%Y-%m-%d')
        if start_data and end_data:
            assert start_data < end_data ,Exception('入住时间有误')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='入住时间有误')

    # 4.通过house_id，判断要提交的房屋是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋数据失败')

    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    # 5.判断当前房屋是否已经被预定了
    try:
        conflict_orders = Order.query.filter(Order.house_id == house_id, end_data > Order.begin_date,
                                             start_data < Order.end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询冲突订单失败')
    if conflict_orders:
        return jsonify(errno=RET.PARAMERR, errmsg='该房屋已经被预订')

    # 6.创建订单模型对象，并赋值
    order = Order()
    order.user_id = g.user_id
    order.house_id = house_id
    order.begin_date = start_data
    order.end_date = end_data
    order.days = (end_data - start_data).days  # days是datetime模块中的属性
    order.house_price = house.price
    order.amount = order.days * house.price

    # 7.将数据保存到数据库
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存订单到数据库失败')

    return jsonify(errno=RET.OK, errmsg='OK')

