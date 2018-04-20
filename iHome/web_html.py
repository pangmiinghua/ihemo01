#coding:utf-8
# 静态html文件处理


from flask import Blueprint,current_app

html_bule = Blueprint('html',__name__)

# 需求1：http://127.0.0.1:5000/register.html
# 需求2：http://127.0.0.1:5000/ ==> 默认加载index.html
   #需要用到路由转换器
# 需求3：http://127.0.0.1:5000/favicon.ico
@html_bule.route('/<re(".*"):file_name>')
def get_static_html(file_name):

    if not file_name:
        file_name = 'index.html'
    # 第三种情况就两句代码
    if file_name != 'favicon.ico':
        file_name = 'html/%s'%file_name


    return current_app.send_static_file(file_name)
    #当视图在执行时，就会有请求，就有current_app请求上下文，其代表当前的app实例
    #send_static_file这是在Flask中的一个底层方法，可以在Flask下点进去查找这个

