#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/1/20 13:19
# @Author  : SongSa
# @Desc    : 
# @File    : activities.py
# @Software: PyCharm
import os
import json
import pymysql
import datetime
import configparser
from lxml import etree
from zhihu_login import login
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

cf = configparser.ConfigParser()
cf.read('conf.ini')
db_host = cf.get('db', 'db_host')
db_user = cf.get('db', 'db_user')
db_pass = cf.get('db', 'db_pass')
db_database = cf.get('db', 'db_database')
activities = cf.get('module','activities')
basic_url = 'https://www.zhihu.com/people/'
header = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
}


def get_username(column_name):
    """
    对数据库中following表的user_name列进行去重查询
    :return:
    """
    db = pymysql.connect(db_host, db_user, db_pass, db_database)
    cursor = db.cursor()
    sql = 'select distinct {0} from following'.format(column_name)
    cursor.execute(sql)
    results = cursor.fetchall()
    db.close()
    return results

def get_mess(url,session,user_name):
    result = session.get(url, headers=header)
    html = result.text
    html = etree.HTML(html)
    data_json = json.loads(html.xpath('//script[@id="js-initialData"]/text()')[0])
    user_details = data_json['initialState']['entities']['users'][user_name]
    try:
        school = user_details['educations'][0]['school']['name']
    except:
        school = ''
    try:
        business = user_details['business']['name']
    except:
        business = ''
    try:
        name = user_details['name']
    except:
        name = ''
    try:
        address = user_details['locations'][0]['name']
    except:
        address = ''
    return name, school, business, address

def insert_mess(user_name, name, school, business, address, url):
    print(user_name, name, school, business, address, url)
    try:
        db = pymysql.connect(db_host, db_user, db_pass, db_database)
        cursor = db.cursor()
        sql = 'insert into activities (user_name, name,school,business,address,url) values ("{0}","{1}","{2}","{3}","{4}","{5}")'.format(user_name, name, school, business, address, url)
        cursor.execute(sql)
        db.commit()
        db.close()
    except Exception as e:
        print("入库失败>>>",e)

if __name__ == '__main__':
    user_Queue = Queue()
    session = login()  # 获取serssion
    results_1 = get_username('user_name')
    for i in results_1:
        user_Queue.put(i[0])
    while True:
        print("当前队列大小：",user_Queue.qsize())
        if user_Queue.empty() == False:
            user_name = user_Queue.get()
            print("当前队列大小：", user_Queue.qsize())
            url = basic_url+user_name+'/'+activities
            print(url)
            name, school, business, address = get_mess(url,session,user_name)
            print('-----------------------------------------------------------------')
            insert_mess(user_name, name, school, business, address,url)
        else:
            break








