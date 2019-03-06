#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/5 22:49
# @Author  : SongSa
# @Desc    : 
# @File    : get_zhihu.py
# @Software: PyCharm
import requests

headers = {
    'authority': 'www.zhihu.com',
    'method': 'GET',
    'scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language':'zh-CN,zh;q=0.8',
    'cookie':'_zap=406c1160-fd16-4735-9cf0-355b2b0c57c7; _xsrf=j6pnyNsW8iEreNza0IaZwvT7owxzg0Al; d_c0="AKCj1maWEw-PTlZ2NeRsHrJ0JOVNYH1GYy8=|1551792533"; capsion_ticket="2|1:0|10:1551792544|14:capsion_ticket|44:ODUyMzc4ZDc4YjA0NGRmMTllNjllNjZkZDFlNTYwODU=|43eb0e9587a10b5641a16ff576f7f7265f1c65ddbce14127b29d2d16889c54af"; z_c0="2|1:0|10:1551792556|4:z_c0|92:Mi4xSDNaOEF3QUFBQUFBb0tQV1pwWVREeVlBQUFCZ0FsVk5yTWRyWFFDYmRaVTJ2cmZpZlVWcWdkcVlCV091OU5NREV3|fdbd1addc5a2b1ced258ee61fea82abfcc6074d3a4e445f94812d326e0baf0a1"; tgw_l7_route=578107ff0d4b4f191be329db6089ff48; tst=r'
    ,'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'
}
result = requests.get('https://www.zhihu.com/people/edit', headers=headers)
print(result.text)