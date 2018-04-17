#coding:utf-8
# 程序入口

from flask import session
from flask_migrate import Migrate,MigrateCommand #用于迁移 mysql数据
from flask_script import Manager   #用于创建管理器管理app项目
from iHome import get_app,db

# 使用工厂设计模式创建app
app = get_app('dev')

# 用代理管理器管理app项目
manager = Manager(app)

# 进行数据库的迁移 把app和db进行关联
Migrate(app,db)
# 将迁移脚本添加到脚本管理器
manager.add_command("db",MigrateCommand)
# 配置完manager后要修改Edit Configcuration中的配置才能重新跑起manager.run()
# 在还没有模型类，没法生成迁移

@app.route("/index" ,methods=["GET","POST"] )
def index():

    session['name'] = 'pmh'  #怎么写了一个这家伙就可以有发送到客户端浏览器了呢？
                                #哪里有弄一个隐藏域发送的代码体现？
    return "index"


if __name__ == '__main__':

    manager.run()
