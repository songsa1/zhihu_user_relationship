#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/1/20 13:19
# @Author  : SongSa
# @Desc    : 
# @File    : activities.py
# @Software: PyCharm
import configparser
import json
import os
import sys

import pymysql
from conn_redis import get_link

from PublicLog import public_log
from MasterFollowing import get_html
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

cf = configparser.ConfigParser()
cf.read('conf.ini')
db_host = cf.get('db', 'db_host')
db_user = cf.get('db', 'db_user')
db_pass = cf.get('db', 'db_pass')
db_database = cf.get('db', 'db_database')
activities = cf.get('module', 'activities')
basic_url = 'https://www.zhihu.com/people/'
headers = {
    'authority': 'www.zhihu.com',
    'method': 'GET',
    'scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'cookie': 'tgw_l7_route=7c109f36fa4ce25acb5a9cf43b0b6415; _xsrf=jKLOKeMr5B7ymogXnWMxzsTI8lovQ7AC; _zap=60785992-3dcd-4133-9d59-36e788a58a82; d_c0="ADAipPkdEw-PTvS2GlazM6BpPtmiDErV8MU=|1551760963"; q_c1=1c472d1aeb5145d9bf0b4eb9d20e9f47|1551760965000|1551760965000'
    ,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
logger = public_log(log_file=os.path.join(BASE_DIR, 'log', 'activities.log'))


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


def get_mess(url, user_name):
    html = get_html(url)
    if html != 0:
        try:
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
            try:
                gender = user_details['gender']
            except:
                gender = ''
            try:
                followerCount = user_details['followerCount']
            except:
                followerCount = 0
            try:
                followingCount = user_details['followingCount']
            except:
                followingCount = 0
            insert_mess(name, school, business, address, gender, followerCount, followingCount, url)
        except Exception as e:
            print("异常>>>" + str(e))


def insert_mess(name, school, business, address, gender, followerCount, followingCount, url):
    try:
        db = pymysql.connect(db_host, db_user, db_pass, db_database)
        cursor = db.cursor()
        sql = 'insert into user_messages (name, school, business, address, gender, followercount, followingCount, url) ' \
              'values ("{0}","{1}","{2}","{3}","{4}","{5}","{6}", "{7}")'.format(name, school, business, address,
                                                                                 gender, followerCount, followingCount,
                                                                                 url)
        try:
            cursor.execute(sql)
            db.commit()
            logger.info("入库成功！")
        except Exception as e:
            logger.info("入库失败>>>" + str(e))
            db.rollback()
        finally:
            db.close()
    except Exception as e:
        logger.info("数据库连接失败" + str(e))


if __name__ == '__main__':
    while True:
        conn = get_link()
        user_name = conn.srandmember(name='TokenBefore', number=1)[0].decode('utf-8')
        url = basic_url + user_name + '/' + activities
        try:
            get_mess(url,user_name)
        except Exception as e:
            logger.info("有异常>>>" + str(e))
            continue
    # t_list = []
    # pool = ThreadPoolExecutor(max_workers=8)
    # while True:
    #     conn = get_link()
    #     wait(t_list, return_when=ALL_COMPLETED)  # 等待子进程结束
    #     for i in range(3):
    #         user_name = conn.srandmember(name='TokenBefore', number=1)[0].decode('utf-8')
    #         url = basic_url + user_name + '/' + activities
    #         try:
    #             t = pool.submit(get_mess, url, user_name)
    #             t_list.append(t)
    #         except Exception as e:
    #             logger.info("有异常>>>" + str(e))
    #             continue
