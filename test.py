#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/2 20:53
# @Author  : SongSa
# @Desc    : 
# @File    : test.py
# @Software: PyCharm

import requests
from PublicLog import public_log
# headers = {
#     'authority': 'www.zhihu.com',
#     'method': 'GET',
#     'scheme': 'https',
#     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#     'cookie': '_xsrf=EBoGl1ayJmZOQctQMax8Iss7SfgGNXof; _zap=5bd4fcbf-017e-469e-bd03-8f53b33804fc; d_c0="ALBkW_QICA-PTkrmznO5tvQqsI1lcRVGjZQ=|1551017256"; tst=r; q_c1=6ff74248ac3845328f2230e8805de0c6|1551017288000|1551017288000; __utmz=155987696.1551017343.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); capsion_ticket="2|1:0|10:1551276947|14:capsion_ticket|44:NzQ2MGRmNjdjYzkzNDdlMDg5YWUxNTg4NmU3YmE1Mzc=|c06b73db85eed390f2f9a1ddc768f5f59b9a9ae3dbcbd154f6e52b6c09bc6bc6"; z_c0="2|1:0|10:1551276956|4:z_c0|92:Mi4xSDNaOEF3QUFBQUFBc0dSYjlBZ0lEeVlBQUFCZ0FsVk5uT2xqWFFDNGpsWklvVDVrcldPa09pQXRGMkRTM1BUaGp3|77a9a62ef859783ed12c3f504d1bb288e33b45a4abbcce2d80138b7799e35485"; tgw_l7_route=6936aeaa581e37ec1db11b7e1aef240e; __utma=155987696.650061337.1551017343.1551107373.1551283620.3; __utmb=155987696.0.10.1551283620'
#     ,
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
# }

# 代理服务器
def get_proxy():
    logger = public_log()
    proxyHost = "http-pro.abuyun.com"
    proxyPort = "9010"
    url = 'https://www.zhihu.com/people/gu-yu-sheng-95-25/following'
    # 代理隧道验证信息
    proxyUser = "H222928065U2443P"
    proxyPass = "81E1DEE0BCA85BAE"

    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }

    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }
    return proxies