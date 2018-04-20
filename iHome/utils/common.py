# coding:utf-8
# 定义公共的工具文件

from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    """"自定义路由转换器，
    根据外界的正则，匹配指定的字符串"""
    def __init__(self,url_map,*args):
        super(RegexConverter,self).__init__(url_map)

        self.regex = args[0]

        # 接下来要到另一个文件导包，不然这文件执行不了