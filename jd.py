import requests
import random
import json
import os
import time
import re
from lxml import etree
from rk import *


url = 'https://passport.jd.com/new/login.aspx'

headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
        'ContentType': 'text/html; charset=utf-8',
		'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8',
		'Connection' : 'keep-alive',
}

s = requests.Session()
s.headers = headers


# 请求登录页面
req1 = s.get(url=url, headers=headers)

sel = etree.HTML(req1.content)
uuid = sel.xpath('//input[@id="uuid"]/@value')[0]

eid = sel.xpath('//input[@id="eid"]/@value')[0]
sa_token = sel.xpath('//input[@id="sa_token"]/@value')[0]
pubKey = sel.xpath('//input[@id="pubKey"]/@value')[0]
t = sel.xpath('//input[@id="token"]/@value')[0]


r = random.random()
login_url = 'https://passport.jd.com/uc/loginService'

class JD(object):

    def __init__(self,username,password,rk_username,rk_pwd):
        self.username = username
        self.password = password
        self.rkclient = RClient(rk_username,rk_pwd)
        self.trackid = ''

    # 账号登录函数
    def login(self):

        params = {

        'uuid':uuid,
        'eid':eid,
        # 'fp':'a2fd52211772d8fea0515bedca560b0b',
        '_t':t,
        'loginType':'c',
        'loginname':self.username,
        'nloginpwd':self.password,
        'chkRememberMe':'',
        'authcode':'',
        'pubKey':pubKey,
        'sa_token':sa_token,
        # 'seqSid':'5574250748814772000'

        }



        headers = {
        'Referer':'https://passport.jd.com/uc/login?ltype=logout',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
        }

        # 验证码图片
        imgcode = 'http:' + sel.xpath('//img[@id="JD_Verification1"]/@src2')[0]
        img = requests.get(imgcode)
        # 把这个路径替换成自己电脑jd.py文件夹的路径，/Users/zhangkai/Desktop/JD
        with open('/Users/zhangkai/Desktop/JD/a.jpg', 'wb') as f:
            f.write(img.content)
        im = open('a.jpg','rb').read()
        print('开始识别验证码...')

        # print(imgcode)   # 手动验证码连接

        # 自动打码
        imgcode1 = self.rkclient.rk_create(im, 3040)['Result']
        print(imgcode1)

  
        if imgcode != '':

            # params['authcode'] = input('请输入验证码：')  # 手动输验证码

            params['authcode'] = str(imgcode1)
            req2 = s.post(login_url, data=params, headers=headers)


            patt = '<Cookie TrackID=(.*?) for .jd.com/>'
            self.trackid = re.compile(patt).findall(str(s.cookies))

            js = json.loads(req2.text[1:-1])


            if js.get('success'):
                print('登录成功')
            else:
                print('登录失败')
        else:
            req2 = s.post(login_url, data=params, headers=headers)

            patt = '<Cookie TrackID=(.*?) for .jd.com/>'
            self.trackid = re.compile(patt).findall(str(s.cookies))

            js = json.loads(req2.text[1:-1])

            if js.get('success'):
                print('登录成功')
            else:
                print('登录失败')

    def addcart(self):

        pid = input('请输入要加入购物车的商品编号：')
        pcount = input('请输入加入数量：')
        add_carturl = 'https://cart.jd.com/gate.action?pid='+pid+'&pcount='+pcount+'&ptype=1'
        # add_carturl = 'https://cart.jd.com/gate.action?pid=3659204&pcount=1&ptype=1'

        req4 = s.get(add_carturl)

        if re.compile('<title>(.*?)</title>').findall(req4.text)[0] == '商品已成功加入购物车':
            print('商品已成功加入购物车')
        else:
            print('添加购物车失败')


    def submit(self):
        #购物车页面
        carturl = 'https://cart.jd.com'
        req5 = s.get(carturl)

        # 取消选择某个商品
        cancelitemurl = 'https://cart.jd.com/cancelItem.action?rd' + str(r)
        form_data = {
                'outSkus':'',
                'pid':'3659204', # 商品id
                'ptype': '1',
                'packId': '0',
                'targetId': '0',
                'promoID': '0',
                'locationId': '1 - 2810 - 6501 - 0'  # 地址代码
        }

        req6 = s.post(cancelitemurl, data=form_data)

        # 选择某个商品
        selectitemurl = 'https://cart.jd.com/selectItem.action?rd' + str(r)
        req7 = s.post(selectitemurl, data=form_data)

        
        timestamp = int(time.time() * 1000)
        # 订单结算页
        orderInfo = 'https://trade.jd.com/shopping/order/getOrderInfo.action?rid=' + str(timestamp)

        # 提交订单url
        submitOrder = 'https://trade.jd.com/shopping/order/submitOrder.action'

        submit_data = {
                'overseaPurchaseCookies':'',
                'submitOrderParam.sopNotPutInvoice':'false',
                'submitOrderParam.trackID': self.trackid[0],
                'submitOrderParam.ignorePriceChange': '0',
                'submitOrderParam.btSupport': '0',
                'submitOrderParam.eid': eid,
                'submitOrderParam.fp': 'b31fc738113fbc4ea5fed9fc9811acc6',
                # 'riskControl': 'D0E404CB705B9732D8D7A53159E363F2140ADCDE164C1F9CABA71F1D7552B70E5C9C6041832CEB4B',
        }



        ordertime = input('''请选择：
                          1.设置下单时间
                          2.选择立即下单
                          请输入选择（1/2):
                          ''')

        if ordertime == '1':
            set_time = input('请按照2017-05-01 23:11:11格式输入下单时间:')
            timeArray = time.mktime(time.strptime(set_time,'%Y-%m-%d %H:%M:%S'))
            while True:
                if time.time() >= timeArray:
                    print(input('大于大于：'))
                    req8 = s.post(submitOrder, data=submit_data)
                    js1 = json.loads(req8.text)
                    print(js1)
                    # 判断是否下单成功
                    if js1['success'] == True:
                        print('下单成功!')
                    else:
                        print('下单失败')
                    break
                else:
                    print('设置时间出错')
                    set_time = input('请按照2017-05-01 23:11:11格式输入下单时间:')
                    continue

        elif ordertime == '2':

            req8 = s.post(submitOrder, data=submit_data)
            js1 = json.loads(req8.text)

            # 判断是否下单成功
            if js1['success'] == True:
                print('下单成功!')
            else:
                print('下单失败')


if __name__ == '__main__':

    jd_user = input('请输入京东账号:')
    jd_pwd = input('请输入京东密码:')
    rk_user = input('请输入若快账号:')
    rk_pwd = input('请输入若快密码:')
    a = JD(jd_user, jd_pwd, rk_user, rk_pwd)
    a.login()
    a.addcart()
    a.submit()

