#coding:utf-8
# 程序入口

from flask_migrate import Migrate,MigrateCommand #用于迁移 mysql数据
from flask_script import Manager   #用于创建管理器管理app项目
from iHome import get_app,db
from iHome import models
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

# 云服务器：
# ip:47.98.185.244(公)172.16.201.49(私有)
# Zhuiyi2282111945

if __name__ == '__main__':
    print app.url_map  #查看路由和视图的匹配关系
    manager.run()
