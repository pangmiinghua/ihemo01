# coding:utf-8
#使用蓝图按照接口版本划分模块


from flask import Blueprint
# url_prefix='/api/1.0'相当于定义版本，url加一个前缀，可以知道了是哪个版本app
api = Blueprint('api_1_0',__name__,url_prefix='/api/1.0')

from . import index,verify,passport
