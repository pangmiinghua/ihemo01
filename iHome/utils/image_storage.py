# coding:utf-8
import qiniu
# 上传图片到七牛云
access_key = 'yV4GmNBLOgQK-1Sn3o4jktGLFdFSrlywR2C-hvsW'
secret_key = 'bixMURPL6tHjrb8QKVg2tm7n9k8C7vaOeQ4MEoeW'
bucket_name = 'ihome'

def upload_image(image_data):

    q = qiniu.Auth(access_key,secret_key)
    token = q.upload_token(bucket_name)
    ret,info = qiniu.put_data(token,None,image_data)

    if info.status_code == 200:
        return  ret.get("key")
    else:
        raise Exception('上传图片失败')


