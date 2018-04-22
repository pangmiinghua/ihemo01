# coding:utf-8
# 定义公共的工具文件
import functools
from flask import session, jsonify,g
from werkzeug.routing import BaseConverter

from iHome.utils.response_code import RET


class RegexConverter(BaseConverter):
    """"自定义路由转换器，
    根据外界的正则，匹配指定的字符串"""
    def __init__(self,url_map,*args):
        super(RegexConverter,self).__init__(url_map)

        self.regex = args[0]

        # 接下来要到另一个文件导包，不然这文件执行不了


def login_required(view_func):
    """"判断用户是否登录"""
    @functools.wraps(view_func)
    def wraaper(*args ,**kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
        else:
            # 当用户已登录，使用g变量记录用户的user_id，方便被装饰器的视图函数中可以直接使用
            g.user_id = user_id
            return view_func(*args ,**kwargs)
    return wraaper