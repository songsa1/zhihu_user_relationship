#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/1/15 18:03
# @Author  : Sa.Song
# @Desc    : 
# @File    : test.py
# @Software: PyCharm


from concurrent.futures import ThreadPoolExecutor

def run(a,b):
    print(b)

if __name__ == '__main__':
    pool = ThreadPoolExecutor(max_workers=3)  # 创建一个容量为3的线程池
    for i in range(3):
        t = pool.submit(run,1,2)  #在线程池中生成三个线程，他们都来调用run方法
    print('我是主线程')