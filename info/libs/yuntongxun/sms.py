# -*- coding:utf-8 -*-

from info.libs.yuntongxun.CCPRestSDK import REST

# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
_accountSid = '8aaf07086521916801652d2332ee0734'

# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
_accountToken = '1d8d4a5bdc71430aa7767bd951ff025e'

# 请使用管理控制台首页的APPID或自己创建应用的APPID
_appId = '8aaf07086521916801652d233340073a'

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

    def send_sms_code(self, to, datas, tempId):
        """
        单例发送短信的方法:需要单例对象才能调用的
        :param to: 发送短信的手机
        :param datas: ['sms_code', 短信提示过期的时间]
        :param tempId: 默认免费的是1
        :return: 如果发送短信成功，返回0；反之，返回-1
        """
        # self ： 代表CCP()初始化出来的单例_instance
        # sendTemplateSMS : 是容联云通讯提供的发送短信的底层方法，我只借用了一下，在外面套了壳子（send_sms_code）
        result = self.rest.sendTemplateSMS(to, datas, tempId)

        if result.get('statusCode') != '000000':
            return -1
        else:
            return 0






#
# if __name__ == '__main__':
#     # 注意： 测试的短信模板编号为1
#     sendTemplateSMS('your mobile number', ['666666', 5], 1)