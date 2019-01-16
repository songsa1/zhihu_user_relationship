#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/1/15 17:26
# @Author  : Sa.Song
# @Desc    : 
# @File    : get_mess.py
# @Software: PyCharm

import json
from lxml import etree
from zhihu_login import login
import pymysql

header = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
}

basic_url = 'https://www.zhihu.com/people/'
start_name = 'deng-tu-zi-38'
url_module = ['activities', 'following', 'followers']  # [用户详情页面、用户关注页面、用户粉丝页面]

user_name_list = []  # 存放用户的username(唯一)

def conn_mysql(user_name):
    db = pymysql.connect('118.24.26.224', 'root', '123456', 'zhihu')
    cursor = db.cursor()
    for i in user_name_list:
        sql = "insert into user_following (user_name,following_name) VALUES ('{0}','{1}')".format(user_name,i)
        try:
            cursor.execute(sql)
            db.commit()
            print('入库成功!')
        except Exception as e:
            print("插入失败>>>",e)



def get_page_num(session,url):  # 获取关注列表的总页数
    num = 0
    result = session.get(url, headers=header)
    html = result.text
    html = etree.HTML(html)
    data_json = json.loads(html.xpath('//script[@id="js-initialData"]/text()')[0])
    try:
        page_button = html.xpath('//div[@class="Pagination"]/button[contains(@class,"PaginationButton") and contains(@class," Button--plain")]')
        page_num = int(page_button[-2].xpath('.//text()')[0])  # 关注列表总页数
    except:
        print('只有一页')
        page_num = 1
    return page_num

def main_logic(session,url,user_name):  # 将关注的username存入user_name_list
    num = 0
    result = session.get(url, headers=header)
    html = result.text
    html = etree.HTML(html)
    data_json = json.loads(html.xpath('//script[@id="js-initialData"]/text()')[0])
    user_details = data_json['initialState']['entities']['users']
    for i in user_details:  # i是各个username
        num += 1
        if num == 1 or i == user_name:
            continue
        else:
            user_name_list.append(i)


def user_detail():  # 使用session循环获取用户username以及用户的关注列表
    session = login()  # 获取serssion
    first_url = basic_url+ start_name+'/'+url_module[2]
    page_num = get_page_num(session,first_url)
    print(page_num)
    user_name = start_name
    for page in range(page_num):
        new_url = 'https://www.zhihu.com/people/{0}/{1}?page={2}'.format(user_name,url_module[2],str(page+1))  #拼接目标url
        #  url拼接原理：原始路径 + username + 页面模块标识 + page
        print(new_url)
        main_logic(session,new_url,user_name)
    # conn_mysql(user_name)  #数据入库



if __name__ == '__main__':
    user_detail()
    print(user_name_list)


    # try:
    #     school = data_json['initialState']['entities']['users']['qi-peng-yu']['educations'][0]['school']['name']
    #     print(school)
    # except:
    #     school = ''
    # try:
    #     business = data_json['initialState']['entities']['users']['qi-peng-yu']['business']['name']
    #     print(business)
    # except:
    #     business = ''
    # try:
    #     name = data_json['initialState']['entities']['users']['qi-peng-yu']['name']
    #     print(name)
    # except:
    #     name = ''
    # try:
    #     address = data_json['initialState']['entities']['users']['qi-peng-yu']['locations'][0]['name']
    #     print(address)
    # except:
    #     address = ''
