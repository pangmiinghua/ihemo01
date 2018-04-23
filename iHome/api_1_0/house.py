# coding:utf-8
from flask import g
from flask import request

from iHome import constants
from iHome import db
from iHome.models import Area, House, Facility, HouseImage
from iHome.utils.image_storage import upload_image
from iHome.utils.response_code import RET
from . import api
from iHome.utils.common import login_required
from flask import current_app,jsonify


@api.route('/houses/image',methods=['POST'])
@login_required
def upload_house_image():
    """"图片上传，会根据是什么房屋的图片--要房屋house_id
    如果都无误则返结果回去"""
    try:
        image_data = request.files.get('house_image')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='图片有误')
    house_id = request.form.get('house_id')
    if not house_id:
        return jsonify(errno=RET.PARAMERR,errmsg='缺少拿必传参数')
    #记住要先有房子才有上传图片，有了房子后保存房屋id到mysql数据库
    #在拿到房屋id后，再到自己的数据库中用这个id去查找，看是否有对应的房屋
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return  jsonify(errno=RET.DBERR,errmsg='查询房屋数据失败')
    if not house:
        return jsonify(errno=RET.NODATA,errmsg='房屋不存在')

    #若查到有此id对应的房屋，则可以上传图片
    try:  #上传图片到七牛云   怎么由七牛云拿到浏览器渲染？
        key = upload_image(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg='上传图片失败')
    #上传了图片之后记得到把这些数据记录下来，以便后面操作

    house_image = HouseImage()   #创建对象，作用用于调用方法
    house_image.house_id = house_id
    house_image.url = key    #这里是表示什么，怎么实现？

    # 设置房屋默认的图片
    if not house.index_image_url:
        house.index_image_url = key

    try:
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存房屋图片数据失败')


    house_image_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK,errmsg='上传图片成功',data={'house_image_url':house_image_url})


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

    # 给facilities属性赋值，实现多对多的关联关系 facility == [2,4,6,8,10]
    facilities = json_dict.get('facility')
    house.facilities = Facility.query.filter(Facility.id.in_(facilities)).all()

    #这一步很关键，要把发布的房屋数据保存到mysql，不然后面的操作都会无法展开
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存新房屋数据失败')

    return jsonify(errno=RET.OK, errmsg='发布新房源成功',
                   data={'house_id':house.id})





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




