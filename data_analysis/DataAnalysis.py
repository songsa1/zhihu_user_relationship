#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/6 19:36
# @Author  : SongSa
# @Desc    : 数据分析
# @File    : DataAnalysis.py
# @Software: PyCharm
import pymysql
import matplotlib as mpl
import matplotlib.pyplot as plt
from pyecharts import Pie
from wordcloud import WordCloud
from PIL import Image
import numpy as np


BUSINESS_LIST = {
    '高新科技': ['互联网', '电子商务', '电子游戏', '计算机软件', '计算机硬件'],
    '信息传媒': ['出版业', '电影录音', '广播电视', '通信'],
    '金融': ['银行', '资本投资', '证券投资', '保险', '信贷', '财务', '审计'],
    '服务业': ['法律', '餐饮', '酒店', '旅游', '广告', '公关', '景观', '咨询分析', '市场推广', '人力资源', '社工服务', '养老服务'],
    '教育': ['高等教育', '基础教育', '职业教育', '幼儿教育', '特殊教育', '培训'],
    '医疗服务': ['临床医疗', '制药', '保健', '美容', '医疗器材', '生物工程', '疗养服务', '护理服务'],
    '艺术娱乐': ['创意艺术', '体育健身', '娱乐休闲', '图书馆', '博物馆', '策展', '博彩'],
    '制造加工': ['食品饮料业', '纺织皮革业', '服装业', '烟草业', '造纸业', '印刷业', '化工业', '汽车', '家具', '电子电器', '机械设备', '塑料工业', '金属加工', '军火'],
    '地产建筑': ['房地产', '装饰装潢', '物业服务', '特殊建造', '建筑设备'],
    '贸易零售': ['零售', '大宗交易', '进出口贸易'],
    '公共服务': ['政府', '国防军事', '航天', '科研', '给排水', '水利能源', '电力电网', '公共管理', '环境保护', '非营利组织'],
    '开采冶金': ['煤炭工业', '石油工业', '黑色金属', '有色金属', '土砂石开采', '地热开采'],
    '交通仓储': ['邮政', '物流递送', '地面运输', '铁路运输', '管线运输', '航运业', '民用航空业'],
    '农林牧渔': ['种植业', '畜牧养殖业', '林业', '渔业']
}


def business_detail_percent(conn, cursor):
    """
    所在行业细分比分比
    :param conn:
    :param cursor:
    :return:
    """
    buss_user_count = dict()
    user_list = list()
    user_num = 0  # 填写了行业信息的用户总数
    top_name = list()  # 行业名称list
    top_num = 0
    top_percent = list()  # 行业人数占比list
    for values in BUSINESS_LIST.values():
        for buss_name in values:
            sql = 'select count(*) from activities where (business = "{0}")'.format(buss_name)
            cursor.execute(sql)
            name_num = cursor.fetchone()[0]
            buss_user_count[buss_name] = name_num
            user_list.append(name_num)
    user_list.sort(reverse=True)
    new_buss_user_count = {v: k for k, v in buss_user_count.items()}  # 将原先字典反转：key:vlaue 对调
    for i in new_buss_user_count:
        user_num += i
    for i in user_list[:10]:
        top_name.append(new_buss_user_count[i])
        top_percent.append(round(i / user_num, 3))
        top_num += i
    top_name.append('其他')
    top_percent.append(round((user_num - top_num) / user_num, 3))
    cursor.close()
    conn.close()
    colors = ['#FF0000', '#FF34B3', '#FF6347', '#FFD39B', '#C67171', '#C1FFC1', '#C0FF3E', '#AB82FF', '#8F8F8F',
              '#515151', '#D6D6D6']
    mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['axes.unicode_minus'] = False
    explode = (0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1)
    plt.pie(top_percent, explode=explode, labels=top_name, autopct='%3.1f%%', startangle=45, shadow=True, colors=colors)
    plt.title("知乎用户所属行业细分top10百分比")
    plt.show()


def business_global_percent(conn, cursor):
    """
    所在行业总分百分比
    :param conn:
    :param cursor:
    :return:
    """
    business_name = list()  # 行业名称
    business_num = list()
    business_percent = list()
    user_num = 0
    for i in BUSINESS_LIST:
        business_name.append(i)
    for values in BUSINESS_LIST.values():
        global_num = 0
        for buss_name in values:
            sql = 'select count(*) from activities where (business = "{0}")'.format(buss_name)
            cursor.execute(sql)
            name_num = cursor.fetchone()[0]
            global_num += name_num
        business_num.append(global_num)
    for i in business_num:
        user_num += i
    for i in business_num:
        business_percent.append(round(i / user_num, 3))
    cursor.close()
    conn.close()
    colors = ['#FF0000', '#FF34B3', '#FF6347', '#FFD39B', '#C67171', '#C1FFC1', '#C0FF3E', '#AB82FF', '#8F8F8F',
              '#515151', '#D6D6D6', '#76EEC6', '#66CDAA', '#3CB371']
    mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['axes.unicode_minus'] = False
    explode = (0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1)
    plt.pie(business_percent, explode=explode, labels=business_name, autopct='%3.1f%%', startangle=45, shadow=True,
            colors=colors)
    plt.title("知乎用户所属行业总分百分比")
    plt.show()


def gender_percent(conn, cursor):
    """
    男女占比
    :param conn:
    :param cursor:
    :return:
    """
    gender_name = ['男', '女', '外星人']
    gender_num = list()
    gender_status = ['1', '0', '-1']
    sql = 'select count(*) from activities'
    cursor.execute(sql)
    user_num = cursor.fetchone()[0]
    for i in gender_status:
        sql = 'select count(*) from activities where (gender = "{0}")'.format(i)
        cursor.execute(sql)
        name_num = cursor.fetchone()[0]
        gender_num.append(round(name_num/user_num, 3))
    cursor.close()
    conn.close()
    colors = ['#FF0000', '#63B8FF', '#dddddd']
    mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['axes.unicode_minus'] = False
    explode = (0.03, 0.03, 0.03)
    plt.pie(gender_num, explode=explode, labels=gender_name, autopct='%3.1f%%', startangle=45, colors=colors)
    plt.title("知乎用户性别比例")
    plt.show()

def school_pie(conn, cursor):
    """
    学历分析饼状图
    :param conn:
    :param cursor:
    :return:
    """
    education_name_list = ['本科及以上', "本科以下"]
    education_num_list = list()
    sql = 'select count(*) from activities where (school != "")'
    cursor.execute(sql)
    user_num = cursor.fetchone()[0]
    sql = 'select count(*) from activities where (school like "%大学%")'
    cursor.execute(sql)
    the_num = cursor.fetchone()[0]
    education_num_list.append(round(the_num/user_num, 3))
    education_num_list.append(round((user_num-the_num)/user_num, 3))
    cursor.close()
    conn.close()
    colors = ['#63B8FF', '#dddddd']
    mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['axes.unicode_minus'] = False
    explode = (0.03, 0.03)
    plt.pie(education_num_list, explode=explode, labels=education_name_list, autopct='%3.1f%%', startangle=45, colors=colors)
    plt.title("知乎用户性别比例")
    plt.show()

def word_cloud_school(conn, cursor):
    """
    学校词云
    :param conn:
    :param cursor:
    :return:
    """
    school_list = list()
    sql = 'select school from activities where (school != "")'
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    for i in result:
        school_list.append(i[0])
    schools = ','.join(school_list)
    img = Image.open('aaa.png')  # 打开图片
    img_array = np.array(img)  # 将图片转换为数组
    wc = WordCloud(
        background_color="white",
        max_words=800,
        font_path='youyuan.TTF',
        mask=img_array,
        prefer_horizontal=0.5,
        min_font_size=10,
        max_font_size=20,
        width=600,
        height=600
    )
    wc.generate(schools)
    wc.to_file('school.png')

def address_word_cloud(conn, cursor):
    """
    居住地分析
    :param conn:
    :param cursor:
    :return:
    """
    address_list = list()
    sql = 'select address from activities where (address != "")'
    cursor.execute(sql)
    result = cursor.fetchall()
    for i in result:
        address_list.append(i[0])
    address = ','.join(address_list)
    img = Image.open('aaa.png')  # 打开图片
    img_array = np.array(img)  # 将图片转换为数组
    wc = WordCloud(
        background_color="white",
        max_words=800,
        font_path='youyuan.TTF',
        mask=img_array,
        prefer_horizontal=0.5,
        min_font_size=11,
        max_font_size=65,
        width=800,
        height=800
    )
    wc.generate(address)
    wc.to_file('address.png')

def address_map(conn, cursor):
    """
    城市地图
    :param conn:
    :param cursor:
    :return:
    """
    address_list = list()
    sql = 'select address from activities where (address != "")'
    cursor.execute(sql)
    result = cursor.fetchall()
    for i in result:
        address_list.append(i[0])
    address = ','.join(address_list)
    print(address)

if __name__ == '__main__':
    conn = pymysql.connect('********', 'root', '**********', 'zhihu')
    cursor = conn.cursor()
    # business_detail_percent(conn, cursor)
    # business_global_percent(conn, cursor)
    # gender_percent(conn, cursor)
    # school_pie(conn, cursor)
    # word_cloud_school(conn, cursor)
    # address_word_cloud(conn, cursor)
    address_map(conn, cursor)