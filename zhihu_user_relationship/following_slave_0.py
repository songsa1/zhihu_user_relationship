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
import configparser
from lxml import etree
from zhihu_login import login
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from conn_redis import get_link

cf = configparser.ConfigParser()
cf.read('conf.ini')
header = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
}
basic_url = 'https://www.zhihu.com/people/'
start_name = cf.get('start_name','start_name')
following = cf.get('module', 'following')
db_host = cf.get('db', 'db_host')
db_user = cf.get('db', 'db_user')
db_pass = cf.get('db', 'db_pass')
db_database = cf.get('db', 'db_database')
q = Queue()

def conn_mysql(user_name, on_name_list):
    """
    循环入库
    :param user_name:
    :param following_dict:
    :return:
    """
    user_list = on_name_list
    for i in user_list:
        sql = "insert into following (user_name,following_name) VALUES ('{0}','{1}')".format(user_name, i)
        try:
            db = pymysql.connect(db_host, db_user, db_pass, db_database)
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print("insert to db is err",str(e))


def get_page_num(session, module_num, user_name=start_name):  # 获取following的总页数
    """
    获取每个用户的following总页数
    :param session:
    :param module_num:
    :param user_name:
    :return:
    """
    first_url = basic_url + user_name + '/' + module_num
    result = session.get(first_url, headers=header)
    if result.status_code == 200:  #根据其返回值代码判断其是否成功请求到目标页面
        html = result.text
        html = etree.HTML(html)
        try:
            page_button = html.xpath('//div[@class="Pagination"]/button[contains(@class,"PaginationButton") and contains(@class," Button--plain")]')
            page_num = int(page_button[-2].xpath('.//text()')[0])  # 关注列表总页数
        except:
            print('只有一页')
            page_num = 1
        return page_num
    else:
        return 0


def main_logic(session, url, user_name, q):
    on_name_list = []  # 方法级list，用来存放当前url获取到的关注者名单，用来和当前用户组成字典，便于入库
    num = 0
    result = session.get(url, headers=header)
    if result.status_code == 200:
        html = result.text
        html = etree.HTML(html)
        data_json = json.loads(html.xpath('//script[@id="js-initialData"]/text()')[0])
        user_details = data_json['initialState']['entities']['users']
        for i in user_details:  # i是各个username
            num += 1
            if num == 1 or i == user_name:
                continue
            else:
                conn = get_link()
                conn.sadd("user_name", i)  # 将用户唯一id存入redis
                on_name_list.append(i)
        return on_name_list
    else:
        return on_name_list


def user_detail(session, user_name=start_name):
    """
    使用session循环获取用户username以及用户的关注列表
    :param session:
    :param q:
    :param user_name:
    :return:
    """
    page_num = get_page_num(session, following, user_name)  # 获取总页数
    if page_num != 0:
        print("用户{0}的following列表页数: {1}".format(user_name,page_num))
        for page in range(page_num):
            new_url = 'https://www.zhihu.com/people/{0}/{1}?page={2}'.format(user_name, following,str(page + 1))  # 拼接目标url
            print("下一步请求的url：%s" % (new_url))
            #  url拼接原理：原始路径 + username + 页面模块标识 + page
            on_name_list = main_logic(session, new_url, user_name, q)
            conn_mysql(user_name, on_name_list)  #将当前following页的关注用户存入数据库
    else:
        print('目标用户following页面请求失败')



if __name__ == '__main__':
    t_list = []
    session = login()  # 获取serssion
    pool = ThreadPoolExecutor(max_workers=12)
    while True:
        wait(t_list, return_when=ALL_COMPLETED)  # 等待子进程结束
        conn = get_link()
        if conn.scard('user_name') != 0:
            for i in range(8):
                name = conn.spop('user_name').decode('utf-8')
                if name != None:
                    t = pool.submit(user_detail, session, name)
                    t_list.append(t)
                else:
                    print("redis中user_name set 为空，程序结束！")
                    break
        else:
            print("redis中user_name set 为空，程序结束！")
            break


