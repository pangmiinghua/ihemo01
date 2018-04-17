# coding:utf-8
# 配置

import redis


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

# 一个项目环境分：开发环境  测试环境  生产环境  要把它分类好
#测试环境和生产环境是同一个数据库
#开发环境和生产环境不是同一个数据库


class Development(Config):
    """开发模式下的配置"""
    pass


class Production(Config):
    """生产环境、线上、部署之后"""

    DEBUG = False   #上线后无需再用True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome_GZ'
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 2  # 有效期为一天


class UnitTest(Config):
    """测试环境"""

    TESTING = True  #改为True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome_unittest'
#   不是说生产环境和测试环境是一个数据库吗？这局句话怎么就？



# 准备工厂要使用的原材料
configs = {
    'dev': Development,
    'pro': Production,
    'test': UnitTest
}