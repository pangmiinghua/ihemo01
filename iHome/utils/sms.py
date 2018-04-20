#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from iHome.libs.yuntongxun.CCPRestSDK import REST
# import ConfigParser

#主帐号
accountSid= '8a216da862dcd1050162e2eb0e350488'

#主帐号Token
accountToken= '9df1949d85b0402b80e7bb8c0d892e90'

#应用Id
appId='8a216da862dcd1050162e2eb0e96048f'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'


class CCP(object):
    """单例"""
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_instance'):
            cls._instance = super(CCP,cls).__new__(cls,*args, **kwargs)

            # 初始化REST SDK
            cls._instance.rest = REST(serverIP,serverPort,softVersion)
            cls._instance.rest.setAccount(accountSid,accountToken)
            cls._instance.rest.setAppId(appId)

        return cls._instance

    def send_sms_code(self, to, datas, tempId):

        result = self.rest.sendTemplateSMS(to, datas, tempId)
        if result.get('statusCode') == '000000':
            return 1
        else:
            return 0





  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id

# def sendTemplateSMS(to,datas,tempId):
#
#
#     #初始化REST SDK
#     rest = REST(serverIP,serverPort,softVersion)
#     rest.setAccount(accountSid,accountToken)
#     rest.setAppId(appId)
#
#     result = rest.sendTemplateSMS(to,datas,tempId)
#     for k,v in result.iteritems():
#
#         if k=='templateSMS' :
#                 for k,s in v.iteritems():
#                     print '%s:%s' % (k, s)
#         else:
#             print '%s:%s' % (k, v)
#
#
# # sendTemplateSMS(手机号码,内容数据,模板Id),['666666','1'] 1表示1分钟后短信过期  另模板默认为1
# sendTemplateSMS(15917350598,['666666','1'],1)