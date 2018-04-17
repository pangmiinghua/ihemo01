#coding:utf-8
import redis   #用于连接及编辑redis数据库
from flask import Flask
from flask import session
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_migrate import Migrate,MigrateCommand  #用于迁移 mysql数据
from flask_script import Manager   #用于创建管理器管理app项目
from flask_sqlalchemy import SQLAlchemy   #用于连接及编辑mysql数据库
import requests

class Config(object):
    """封装配置的类"""
    DEBUG = True
    # 把SQLAlchemy配置上使用mysql
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/iHome"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置redis数据库 写法结构完全是模仿Django模式来写的
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # 配置密钥
    SECRET_KEY = 'q7pBNcWPgmF6BqB6b5VICF7z7pI+90o0O4CaJsFGjzRsYiya9SEgUDytXvzFsIaR'

    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 3600 * 2  #两小时

app = Flask(__name__)

# 用于加载配置参数  在写Config（）类时先写这个表明
app.config.from_object(Config)
# 注意：先有配置 再有创建链接到数据库的对象
db = SQLAlchemy(app)

# 开始CSRF保护：flask需要自己将csrf_token写入浏览器的cookie
CSRFProtect(app)



# 创建链接到redis数据库的对象  Config.REDIS_HOST从Config中读取REDIS_HOST
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 记得要开始redis数据库

# 用代理管理器管理app项目
manager = Manager(app)

# 进行数据库的迁移 把app和db进行关联
Migrate(app,db)
# 将迁移脚本添加到脚本管理器
manager.add_command("db",MigrateCommand)
# 配置完manager后要修改Edit Configcuration中的配置才能重新跑起manager.run()
# 在还没有模型类，没法生成迁移


Session(app)


@app.route("/index" ,methods=["GET","POST"] )
def index():

    session['name'] = 'pmh'

    return "index"


if __name__ == '__main__':

    manager.run()
