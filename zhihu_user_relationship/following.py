# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# # @Time    : 2019/1/15 17:26
# # @Author  : Sa.Song
# # @Desc    :
# # @File    : following.py
# # @Software: PyCharm
#
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
header = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
}
basic_url = 'https://www.zhihu.com/people/'
# start_name = 'zuo-wo-12'
start_name = 'deng-tu-zi-38'
following = cf.get('module', 'following')
db_host = cf.get('db', 'db_host')
db_user = cf.get('db', 'db_user')
db_pass = cf.get('db', 'db_pass')
db_database = cf.get('db', 'db_database')
user_name_list = []  # 存放用户的username(唯一)
q = Queue()
on_name_list = []  # 方法级list，用来存放当前url获取到的关注者名单，用来和当前用户组成字典，便于入库


def conn_mysql(user_name, following_dict):
    """
    循环入库
    :param user_name:
    :param following_dict:
    :return:
    """
    user_list = following_dict[user_name]
    for i in user_list:
        sql = "insert into following (user_name,following_name) VALUES ('{0}','{1}')".format(user_name, i)
        try:
            db = pymysql.connect(db_host, db_user, db_pass, db_database)
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            pass


def get_page_num(session, module_num, user_name=start_name):  # 获取following的总页数
    """
    获取每个用户的following总页数
    :param session:
    :param module_num:
    :param user_name:
    :return:
    """
    try:
        num = 0
        first_url = basic_url + user_name + '/' + module_num
        result = session.get(first_url, headers=header)
        html = result.text
        html = etree.HTML(html)
        try:
            page_button = html.xpath('//div[@class="Pagination"]/button[contains(@class,"PaginationButton") and contains(@class," Button--plain")]')
            page_num = int(page_button[-2].xpath('.//text()')[0])  # 关注列表总页数
        except:
            print('只有一页')
            page_num = 1
    except Exception as e:
        print('>>>1', e)
    return page_num


def main_logic(session, url, user_name, q):  # 将关注的username存入user_name_list
    """
    将关注的username存入队列，user_name_list列表来进行去重
    :param session: session
    :param url: 每一个following页url
    :param user_name:
    :param q: 队列
    :return:
    """
    following_dict = {}  # {"用户":"关注的用户"}
    num = 0
    result = session.get(url, headers=header)
    html = result.text
    html = etree.HTML(html)
    try:
        data_json = json.loads(html.xpath('//script[@id="js-initialData"]/text()')[0])
        user_details = data_json['initialState']['entities']['users']
        for i in user_details:  # i是各个username
            num += 1
            if num == 1 or i == user_name:
                continue
            else:
                if i in user_name_list:
                    continue
                else:
                    user_name_list.append(i)
                    q.put(i, block=True)  # 将user_name放入队列
                    on_name_list.append(i)
    except Exception as e:
        print(e)
        print('----------------')
    following_dict[user_name] = on_name_list
    return following_dict


def user_detail(session, q, user_name=start_name):
    """
    使用session循环获取用户username以及用户的关注列表
    :param session:
    :param q:
    :param user_name:
    :return:
    """
    try:
        page_num = get_page_num(session, following, user_name)  # 获取总页数
        # print("用户{0}的following列表页数: {1}".format(user_name,page_num))
        for page in range(page_num):
            new_url = 'https://www.zhihu.com/people/{0}/{1}?page={2}'.format(user_name, following,str(page + 1))  # 拼接目标url
            print("下一步请求的url：%s" % (new_url))
            #  url拼接原理：原始路径 + username + 页面模块标识 + page
            following_dict = main_logic(session, new_url, user_name, q)
            conn_mysql(user_name, following_dict)
            # print("当前队列大小为：",q.qsize())
            on_name_list.clear()
            following_dict.clear()
    except Exception as e:
        print("异常", e)


if __name__ == '__main__':
    t_list = []
    session = login()  # 获取serssion
    user_detail(session, q)
    pool = ThreadPoolExecutor(max_workers=12)
    try:
        while True:
            wait(t_list, return_when=ALL_COMPLETED)  # 等待子进程结束
            if q.empty() == False:
                for i in range(8):
                    name = q.get()
                    t = pool.submit(user_detail, session, q, name)
                    t_list.append(t)
            else:
                break
    except Exception as e:
        print("抓了一个异常>>>", e)
    print('user_name_list列表长度：' + str(len(user_name_list)))
    print(datetime.datetime.now())
