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
activities = cf.get('module','activities')
basic_url = 'https://www.zhihu.com/people/'
headers = {
    'authority':'www.zhihu.com',
    'method':'GET',
    'scheme':'https',
    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'cookie':'_xsrf=EBoGl1ayJmZOQctQMax8Iss7SfgGNXof; _zap=5bd4fcbf-017e-469e-bd03-8f53b33804fc; d_c0="ALBkW_QICA-PTkrmznO5tvQqsI1lcRVGjZQ=|1551017256"; tst=r; q_c1=6ff74248ac3845328f2230e8805de0c6|1551017288000|1551017288000; __utmz=155987696.1551017343.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); anc_cap_id=0365d898dc274aceadac523339b0c3de; __utma=155987696.650061337.1551017343.1551017343.1551107373.2; __utmc=155987696; tgw_l7_route=578107ff0d4b4f191be329db6089ff48'
    ,'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
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
                diploma_list = list()
                educations = user_details['educations']
                for i in educations:
                    diploma = i['diploma']
                    print(diploma)
                    diploma_list.append(diploma)

                # business = user_details['business']['name']
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
            followerCount = user_details['followerCount']
            followingCount = user_details['followingCount']

            insert_mess(name, school, business, address, gender, url)
        except Exception as e:
                print("异常>>>"+str(e))


def insert_mess(name, school, business, address, gender, url):
    try:
        db = pymysql.connect(db_host, db_user, db_pass, db_database)
        cursor = db.cursor()
        sql = 'insert into activities (name, school, business, address, gender, url) values ("{0}","{1}","{2}","{3}","{4}","{5}")'.format(name, school, business, address, gender,url)
        try:
            cursor.execute(sql)
            db.commit()
            logger.info("入库成功！")
        except Exception as e:
            logger.info("入库失败>>>"+str(e))
            db.rollback()
        finally:
            db.close()
    except Exception as e:
        logger.info("数据库连接失败"+str(e))

if __name__ == '__main__':
    t_list = []
    pool = ThreadPoolExecutor(max_workers=8)
    while True:
        conn = get_link()
        wait(t_list, return_when=ALL_COMPLETED)  # 等待子进程结束
        for i in range(4):
            user_name = conn.srandmember(name='TokenBefore', number=1)[0].decode('utf-8')
            url = basic_url+user_name+'/'+activities
            try:
                t = pool.submit(get_mess, url, user_name)
                t_list.append(t)
            except Exception as e:
                logger.info("有异常>>>"+str(e))
                continue







