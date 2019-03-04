#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/2/25 21:27
# @Author  : SongSa
# @Desc    : 
# @File    : PublicLog.py.py
# @Software: PyCharm
import logging
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
def public_log(log_file=os.path.join(BASE_DIR, 'log', 'zhihu-log.log'),
               logger_name='default-log',
               level=logging.DEBUG
               ):

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)   # 添加日志等级

    # 创建控制台 console handler
    ch = logging.StreamHandler()
        # 设置控制台输出时的日志等级
    ch.setLevel(logging.CRITICAL)

    # 创建文件 handler
    fh = logging.FileHandler(filename=log_file, encoding='utf-8')
        # 设置写入文件的日志等级
    fh.setLevel(logging.DEBUG)
    # 创建 formatter
    formatter = logging.Formatter('%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s')

    # 添加formatter
    # ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # 把ch fh 添加到logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
