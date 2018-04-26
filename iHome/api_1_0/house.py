# coding:utf-8
from flask import g
from flask import request
from flask import session

from iHome import constants, redis_store
from iHome import db
from iHome.models import Area, House, Facility, HouseImage
from iHome.utils.image_storage import upload_image
from iHome.utils.response_code import RET
from . import api
from iHome.utils.common import login_required
from flask import current_app,jsonify







@api.route("/houses/search",methods=['GET'])
def get_house_search():
    """"查询所有房屋信息
    需求1：无条件查询所有的房屋数据
    需求2：根据城区搜索房屋
    0.获取搜索使用的参数
    1.直接查询所有房屋数据
    2.构造房屋数据
    3.响应房屋数据
    """
    # 在数据库拿出所有房屋信息

    # 获取城区信息
    aid = request.args.get('aid')

    # sk = request.args.get('sk','')
    # current_app.logger.error(sk)


    try:
        # 得到BeseQuery对象
        house_query = House.query
        # 根据城区信息搜索房屋
        if aid:
            house_query = house_query.filter(House.area_id == aid)
        houses = house_query.all()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg='查询房屋数据失败')

    house_dict_list = []
    for house in houses:
        house_dict_list.append(house.to_basic_dict())


    return jsonify(errno=RET.OK,errmsg='OK',data=house_dict_list)


# 主页房屋推荐：推荐最新发布的五个房屋
@api.route('/houses/index',methods=['GET'])
def get_house_index():
    """主页房屋推荐:推荐最新发布的五个房屋
        1.直接查询最新发布的五个房屋：根据创建的时间倒叙，取最前面五个
        2.构造房屋推荐数据
        3.响应房屋推荐数据
        """
    try:
        houses = House.query.order_by(House.create_time.desc()).\
            limit(constants.HOME_PAGE_MAX_HOUSES)
    except Exception as e:
        current_app.loger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋推荐数据失败')
    # 构造房屋推荐数据
    house_dict_list = []
    for house in houses:
        house_dict_list.append(house.to_basic_dict())  #调用model处的函数把

    return jsonify(errno=RET.OK, errmsg='OK', data=house_dict_list)


# """通过房屋id查看房屋详情"""
@api.route('/houses/<int:house_id>',methods=['GET'])
def get_house_detail(house_id):
    """通过房屋id查看房屋详情"""
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询房屋数据失败')
    if not house:
        return jsonify(errno=RET.NODATA,errmsg='房屋不存在')
    #构造房屋详情响应数据  ？
    # response_dict = house.to_full_dict()
    response_house_detail = house.to_full_dict()
    # 尝试获取登录用户信息：可能是未登录的
    login_user_id = session.get('user_id', -1)

    return jsonify(errno=RET.OK,errmsg='OK',
                   data=response_house_detail,login_user_id = login_user_id)



@api.route('/houses/image',methods=['POST'])
@login_required
def upload_house_image():
    """图片上传，会根据是什么房屋的图片--要房屋house_id
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
    try:  #上传图片到七牛云   怎么由七牛云拿到浏览器渲染？ 在前端代码写上下载图片的地址
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
    """提供城区信息    将城区信息提供给主页的中的   需要一个列表：向视图
    1.直接查询所有城区信息
    2.构造城区信息响应数据
    3.响应城区信息
    """

    # 在查询数据库之前读取缓存的城区信息
    # 现在的代码形式：
    try:
        area_dict_list = redis_store.get('Areas')   #查
        if area_dict_list:
            return jsonify(errno=RET.OK, errmsg='OK', data=eval(area_dict_list))
    except Exception as e:
        current_app.logger.error(e)



    # 原来的代码形式：
    try:
        areas = Area.query.all()  #获取所有城区信息   areas里面存的是Area的模型对象
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询地区数据失败')

    # 2、构造城区信息响应数据，将aresa转成字典列表
    area_dict_list = []
    for area in areas:
        area_dict_list.append(area.to_dict())

    try:      #键：Areas    值：area_dict_list     缓存时间：constants.AREA_INFO_REDIS_EXPIRES
        redis_store.set("Areas",area_dict_list,constants.AREA_INFO_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)

    # 响应城区信息：jsonify只认识字典或字典列表，所以把data中的内容都转换成了字典列表
    return jsonify(errno=RET.OK,errmsg='OK',data=area_dict_list)




# 在做视图时先看是用户发什么请求：post  get   put  delede
# 对于返回去jsonify是字典或字典列表

# 数据，有关系型和非关系型，编程语言用它们。通过映射关系，django中通过ROM操作
# mysql，flask中通过    操作mysql，，它们储存的方式由自身类型决定，而在取出用时
# 可以随意拼接成不同形式，如字典、如列表、字典列表、、、多种多样，数据同时还可通过各种
# 函数转换，得到不同类型从而便于被特定的情况使用，如jsonify中要的是字典或字典列表

# 另非关系型如redis：储存是键值对，那样取的时候也是一样，也可拼接。
# redis_store.set("Areas",area_dict_list)


# 数据有获取和写入
# redis_store  用写入：set:存储字符串。hset：存储hash。lpush:列表   获取：
# mysql：db.session.set/get
#       :db.session.commit()

# 对于get请求：
#         把数据进行构造成字典或字典列表   再返回
#             其中构造部分有的可以在model中写（利用代码高内聚），视图中调用

# post请求有的是修改数据，或是传入数据，这时是先判断数据是否合法，接下是
# 看什么情况存在redis/mysql   再返回
