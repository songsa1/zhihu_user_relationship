#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/16 17:18
# @Author  : Sa.Song
# @Desc    : 
# @File    : YDM.py
# @Software: PyCharm

import json
import time
import requests

class YDMHttp:
    apiurl = 'http://api.yundama.com/api.php'
    username = 'songsongsong'
    password = '*hs19931221*'
    appid = '6209'
    appkey = '0f8f9bb71e494ae7a97fd877bb639075'

    def __init__(self, username, password, appid, appkey):
        self.username = username
        self.password = password
        self.appid = str(appid)
        self.appkey = appkey

    def request(self, fields, files=[]):
        response = self.post_url(self.apiurl, fields, files)
        response = json.loads(response)
        return response

    def balance(self):
        data = {'method': 'balance', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if response:
            if response['ret'] and response['ret'] < 0:
                return response['ret']
            else:
                return response['balance']
        else:
            return -9001

    def login(self):
        data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if response:
            if response['ret'] and response['ret'] < 0:
                return response['ret']
            else:
                return response['uid']
        else:
            return -9001

    def upload(self, filename, codetype, timeout):
        data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout)}
        file = {'file': filename}
        response = self.request(data, file)
        if response:
            if response['ret'] and response['ret'] < 0:
                return response['ret']
            else:
                return response['cid']
        else:
            return -9001

    def result(self, cid):
        data = {'method': 'result', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'cid': str(cid)}
        response = self.request(data)
        return response and response['text'] or ''

    def decode(self, filename, codetype, timeout):
        cid = self.upload(filename, codetype, timeout)
        if cid > 0:
            for i in range(0, timeout):
                result = self.result(cid)
                if result != '':
                    return cid, result
                else:
                    time.sleep(1)
            return -3003, ''
        else:
            return cid, ''

    def report(self, cid):
        data = {'method': 'report', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'cid': str(cid), 'flag': '0'}
        response = self.request(data)
        if response:
            return response['ret']
        else:
            return -9001

    def post_url(self, url, fields, files=[]):
        for key in files:
            files[key] = open(files[key], 'rb')
        res = requests.post(url, files=files, data=fields)
        return res.text

def use_ydm(filename):
    username = YDMHttp.username # 用户名
    password = YDMHttp.password  # 密码
    app_id = YDMHttp.appid  # 软件ID
    app_key = YDMHttp.appkey  # 软件密钥
    code_type = 1004  # 验证码类型
    timeout = 60  # 超时时间，秒
    yundama = YDMHttp(username, password, app_id, app_key)  # 初始化
    balance = yundama.balance()  # 查询余额
    print('您的题分余额为{}'.format(balance))
    cid, result = yundama.decode(filename, code_type, timeout)  # 开始识别
    print('识别结果为{}'.format(result))
    return result
