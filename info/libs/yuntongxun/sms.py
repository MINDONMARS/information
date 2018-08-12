# -*- coding:utf-8 -*-

from info.libs.yuntongxun.CCPRestSDK import REST

# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
_accountSid = '8aaf070862181ad5016236f3bcc811d5'

# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
_accountToken = '4e831592bd464663b0de944df13f16ef'

# 请使用管理控制台首页的APPID或自己创建应用的APPID
_appId = '8aaf070862181ad5016236f3bd2611dc'

# 说明：请求地址，生产环境配置成app.cloopen.com
_serverIP = 'sandboxapp.cloopen.com'

# 说明：请求端口 ，生产环境为8883
_serverPort = "8883"

# 说明：REST API版本号保持不变
_softVersion = '2013-12-26'

# 云通讯官方提供的发送短信代码实例
# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id
# def sendTemplateSMS(to, datas, tempId):
#     # 初始化REST SDK
#     rest = REST(_serverIP, _serverPort, _softVersion)
#     rest.setAccount(_accountSid, _accountToken)
#     rest.setAppId(_appId)
#
#     result = rest.sendTemplateSMS(to, datas, tempId)
#     for k, v in result.items():
#
#         if k == 'templateSMS':
#             for k, s in v.iteritems():
#                 print('%s:%s' % (k, s))
#         else:
#             print('%s:%s' % (k, v))


class CCP(object):
    """封装单例类发送短信验证码"""
    def __new__(cls, *args, **kwargs):
        # 判断_instance对象是否存在, 如果存在,就不再重复的创建对象, 如果不存就创建一个_instanc对象
        if not hasattr(cls, '_instance'):
            cls._instansce = super(CCP, cls).__new__(cls, *args, **kwargs)

            # 搭配单例让, rest对象只实例化一次
            rest = REST(_serverIP, _serverPort, _softVersion)
            # 给_instance单例动态的绑定一个rest属性, 属性保存到rest对象
            cls._instansce.rest = rest

            cls._instansce.rest.setAccount(_accountSid, _accountToken)
            cls._instansce.rest.setAppId(_appId)

        return cls._instansce









if __name__ == '__main__':
    # 注意： 测试的短信模板编号为1
    sendTemplateSMS('your mobile number', ['666666', 5], 1)