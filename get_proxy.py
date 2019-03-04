#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/2/27 23:23
# @Author  : SongSa
# @Desc    : 
# @File    : get_proxy.py
# @Software: PyCharm
import json

import requests

from PublicLog import public_log

api = 'http://ged.ip3366.net/api/?key=20190227232137630&getnum=5&order=1&formats=2&proxytype=1'
headers = {
    'method':'GET',
    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'cookie':'UM_distinctid=1692f8296f449c-0993c1132f6212-1333062-1fa400-1692f8296f568e; ASPSESSIONIDSSAADDSB=HBMEGOODOCBBPMBOGJDBEIFP'
    ,'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
}
logger = public_log()
def get_proxy():
    result = json.loads(requests.get(api,headers=headers).text)[0]
    proxy = str(result['Ip'])+':'+str(result['Port'])
    proxies = {
        'https':proxy
    }
    logger.debug("调用代理IP>>>"+str(proxies))
    return proxies

# url = 'https://www.zhihu.com/people/deng-tu-zi-38/following'
# proxy = get_proxy()
# result = requests.get(url,headers=headers, proxies=proxy)
# print(result.status_code)
# print(result.text)