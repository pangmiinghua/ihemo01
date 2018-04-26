# coding:utf-8
import datetime

from flask import g
from flask import request, jsonify,current_app

from iHome import db
from iHome.models import House, Order
from iHome.utils.response_code import RET
from . import api
from iHome.utils.common import login_required



@api.route('/orders',methods=['GET'])
@login_required
def get_order_list():
    """我的订单，客户订单  两个都在一个接口查
        0.判断用户是否登录
        1.获取当前登录用户的user_id
        2.使用user_id查询用户的所有的订单信息
        3.构造响应数据
        4.响应数据
        """
    # 接受用户身份信息
    role = request.args.get('role')
    if role not in ['custom', 'landlord']:
        return jsonify(errno=RET.PARAMERR, errmsg='用户身份错误')

    # 1.获取当前登录用户的user_id
    user_id = g.user_id

    # 2.使用user_id查询用户的所有的订单信息
    try:
        if role == 'custom': # 查询我的订单：我下了谁的订单
            orders = Order.query.filter(Order.user_id==user_id).all()
        else:  # 客户订单：查询谁下了我的订单
            # 获取该用户发布的房屋
            houses = House.query.filter(House.user_id == user_id).all()
            # 收集发布的房屋的house_ids
            house_ids = [house.id for house in houses]
            # 将在订单中的房屋对应的订单查询出来
            orders = Order.query.filter(Order.house_id.in_(house_ids)).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户订单数据失败')

    # 3.构造响应数据
    order_dict_list = []
    for order in orders:
        order_dict_list.append(order.to_dict())

    return jsonify(errno=RET.OK, errmsg='OK', data=order_dict_list)



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

