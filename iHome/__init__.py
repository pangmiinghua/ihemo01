# coding:utf-8
# 创建应用实例  这里的代码是要用于测试的 这里相当于第一个业务逻辑
# 这里的是业务逻辑 在项目在manager一开始执行时，会跑到iHome中的__init__初始化文件
import redis   #用于连接及编辑redis数据库
from flask import Flask    #导入Flask环境
from flask_session import Session   #使用Session使得数据保存在数据库  而导包session用于session操作数据，数据一般在cookie
from flask_wtf import CSRFProtect   #开启保护
from flask_sqlalchemy import SQLAlchemy   #用于连接及编辑mysql数据库
from config import configs  #导入配置文件的“原材料”
from iHome.utils.common import RegexConverter
import logging
from logging.handlers import RotatingFileHandler


db = SQLAlchemy()
# redis_store = redis.StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)
redis_store = None
def setUpLogging(level):
    # 设置日志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def get_app(config_name):
    """"对于这里其功能相当于：当把什么数据（原材料(这里指不同的模块,如测试模块、生产模块，放入不同模块iHome就运行不同环境)）
    放进来，我就根据这些原材料生产出什么信息（功能），然后你就可以在manager程序入口文件使用这个功能）"""


    # 根据开发环境设置日记等级  根据传进来的不同config_name类来获取不同等级LOGGING_LEVEL
    setUpLogging(configs[config_name].LOGGING_LEVEL)

    app = Flask(__name__)

    # 用于加载配置参数  在写Config（）类时先写这个表明
    app.config.from_object(configs[config_name])
    # 注意：先有配置 再有创建链接到数据库的对象
    # db = SQLAlchemy(app)
    db.init_app(app)
    # 开始CSRF保护：flask需要自己将csrf_token写入浏览器的cookie
    CSRFProtect(app)

    global redis_store
    # 创建链接到redis数据库的对象  Config.REDIS_HOST从Config中读取REDIS_HOST
    redis_store = redis.StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)
    # 记得要开始redis数据库,以后可以根据现实需求用redis_store把一下数据放进redis数据库

    # 使用flask_session扩展存储session到Redis数据库
    Session(app)

    # 注意：需要先有正则转换器，才能匹配路由，所以不在52行写
    # 将自定义的路由转换器加到转换器列表
    app.url_map.converters['re'] = RegexConverter

    # 哪里创建就哪里导入，这样可以防止某些数据的丢失
    from iHome.api_1_0 import api
    # 注册api蓝图  为何？ 因为app里面不知道api的存在，所以要
    app.register_blueprint(api)

    from iHome.web_html import html_bule

    app.register_blueprint(html_bule)




    return app