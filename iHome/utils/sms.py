#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from iHome.libs.yuntongxun.CCPRestSDK import REST
# import ConfigParser

#���ʺ�
accountSid= '8a216da862dcd1050162e2eb0e350488'

#���ʺ�Token
accountToken= '9df1949d85b0402b80e7bb8c0d892e90'

#Ӧ��Id
appId='8a216da862dcd1050162e2eb0e96048f'

#�����ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com'

#����˿� 
serverPort='8883'

#REST�汾��
softVersion='2013-12-26'


class CCP(object):
    """����"""
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_instance'):
            cls._instance = super(CCP,cls).__new__(cls,*args, **kwargs)

            # ��ʼ��REST SDK
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





  # ����ģ�����
  # @param to �ֻ�����
  # @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
  # @param $tempId ģ��Id

# def sendTemplateSMS(to,datas,tempId):
#
#
#     #��ʼ��REST SDK
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
# # sendTemplateSMS(�ֻ�����,��������,ģ��Id),['666666','1'] 1��ʾ1���Ӻ���Ź���  ��ģ��Ĭ��Ϊ1
# sendTemplateSMS(15917350598,['666666','1'],1)