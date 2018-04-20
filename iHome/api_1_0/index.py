# coding:utf-8
# 模拟主页逻辑
from . import api
from iHome import redis_store

# 需求1：http://127.0.0.1:5000/register.html
# 需求2：http://127.0.0.1:5000/ ==> 默认加载index.html
# 需求3：http://127.0.0.1:5000/favicon.ico
@api.route("/index",methods=["GET","POST"] )
def index():

    redis_store.set('name','pmh')
    # session['name'] = 'pmh'  #怎么写了一个这家伙就可以有发送到客户端浏览器了呢？
                   #哪里有弄一个隐藏域发送的代码体现？
    return "index"