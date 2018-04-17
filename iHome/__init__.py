# coding:utf-8
# 创建应用实例  这里的代码是要用于测试的 这里相当于第一个业务逻辑
# 这里的是业务逻辑 在项目在manager一开始执行时，会跑到iHome中的__init__初始化文件

import redis   #用于连接及编辑redis数据库
from flask import Flask
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy   #用于连接及编辑mysql数据库
from config import configs

db = SQLAlchemy()
def get_app(config_name):

    app = Flask(__name__)

    # 用于加载配置参数  在写Config（）类时先写这个表明
    app.config.from_object(configs[config_name])
    # 注意：先有配置 再有创建链接到数据库的对象
    # db = SQLAlchemy(app)
    db.init_app(app)
    # 开始CSRF保护：flask需要自己将csrf_token写入浏览器的cookie
    CSRFProtect(app)

    # 创建链接到redis数据库的对象  Config.REDIS_HOST从Config中读取REDIS_HOST
    redis_store = redis.StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)
    # 记得要开始redis数据库

    # 使⽤用flask_session扩展存储session到Redis数据库
    Session(app)

    return app