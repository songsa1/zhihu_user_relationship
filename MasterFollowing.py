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
import requests
import configparser
from lxml import etree
from config.log import public_log
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from conn_redis import get_link
from get_proxy import get_proxy

cf = configparser.ConfigParser()
cf.read('conf.ini')
headers = {
    'authority':'www.zhihu.com',
    'method':'GET',
    'scheme':'https',
    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'cookie':'_xsrf=EBoGl1ayJmZOQctQMax8Iss7SfgGNXof; _zap=5bd4fcbf-017e-469e-bd03-8f53b33804fc; d_c0="ALBkW_QICA-PTkrmznO5tvQqsI1lcRVGjZQ=|1551017256"; tst=r; q_c1=6ff74248ac3845328f2230e8805de0c6|1551017288000|1551017288000; __utmz=155987696.1551017343.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); capsion_ticket="2|1:0|10:1551276947|14:capsion_ticket|44:NzQ2MGRmNjdjYzkzNDdlMDg5YWUxNTg4NmU3YmE1Mzc=|c06b73db85eed390f2f9a1ddc768f5f59b9a9ae3dbcbd154f6e52b6c09bc6bc6"; z_c0="2|1:0|10:1551276956|4:z_c0|92:Mi4xSDNaOEF3QUFBQUFBc0dSYjlBZ0lEeVlBQUFCZ0FsVk5uT2xqWFFDNGpsWklvVDVrcldPa09pQXRGMkRTM1BUaGp3|77a9a62ef859783ed12c3f504d1bb288e33b45a4abbcce2d80138b7799e35485"; tgw_l7_route=6936aeaa581e37ec1db11b7e1aef240e; __utma=155987696.650061337.1551017343.1551107373.1551283620.3; __utmb=155987696.0.10.1551283620'
    ,'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
}
basic_url = 'https://www.zhihu.com/people/'
start_name = cf.get('start_name','start_name')
following = cf.get('module', 'following')
db_host = cf.get('db', 'db_host')
db_user = cf.get('db', 'db_user')
db_pass = cf.get('db', 'db_pass')
db_database = cf.get('db', 'db_database')
logger = public_log()


def get_page_num(module_num, user_name=start_name):  # 获取following的总页数
    """
    获取每个用户的following总页数
    :param session:
    :param module_num:
    :param user_name:
    :return:
    """
    first_url = basic_url + user_name + '/' + module_num
    result = requests.get(first_url, headers=headers)
    if result.status_code != 200:  #根据其返回值代码判断其是否成功请求到目标页面
        proxy = get_proxy()
        result = requests.get(first_url, headers=headers, proxies=proxy)
    html = etree.HTML(result.text)
    if html.xpath('//title/text()')[0] == '安全验证 - 知乎':
        proxy = get_proxy()
        result = requests.get(first_url, headers=headers, proxies=proxy)
        html = etree.HTML(result.text)
    try:
        page_button = html.xpath('//div[@class="Pagination"]/button[contains(@class,"PaginationButton") and contains(@class," Button--plain")]')
        page_num = int(page_button[-2].xpath('.//text()')[0])  # 关注列表总页数
    except Exception as e:
        logger.error(first_url)
        logger.info("该用户关注者列表只有一页，用户舍弃>>>")
        page_num = 0
    return page_num

def main_logic(url, user_name):
    num = 0
    result = requests.get(url, headers=headers)
    if result.status_code != 200:  #根据其返回值代码判断其是否成功请求到目标页面
        proxy = get_proxy()
        result = requests.get(url, headers=headers, proxies=proxy)
    html = etree.HTML(result.text)
    if html.xpath('//title/text()')[0] == '安全验证 - 知乎':
        proxy = get_proxy()
        result = requests.get(url, headers=headers, proxies=proxy)
        html = etree.HTML(result.text)
    try:
        data_json = json.loads(html.xpath('//script[@id="js-initialData"]/text()')[0])
        user_details = data_json['initialState']['entities']['users']
        conn = get_link()
        for i in user_details:  # i是各个username
            num += 1
            if num == 1 or i == user_name:
                continue
            else:
                try:
                    conn.sadd("user_name", i)  # 将用户唯一id存入redis
                    logger.info("{0} 入库".format(i))
                except Exception as e:
                    logger.info("user_name插入redis时出现异常>>>", str(e))
    except Exception as e:
        logger.info("获取用户关注详情失败>>>"+str(e))

def user_detail(user_name=start_name):
    page_num = get_page_num(following, user_name)  # 获取总页数
    if page_num:
        for page in range(page_num):
            new_url = 'https://www.zhihu.com/people/{0}/{1}?page={2}'.format(user_name, following,str(page + 1))  # 拼接目标url
            #  url拼接原理：原始路径 + username + 页面模块标识 + page
            main_logic(new_url, user_name)




if __name__ == '__main__':
    t_list = []
    user_detail()
    pool = ThreadPoolExecutor(max_workers=8)
    while True:
        wait(t_list, return_when=ALL_COMPLETED)  # 等待子进程结束
        conn = get_link()
        if  conn.scard('user_name'):
            for i in range(4):
                try:
                    name = conn.srandmember(name='user_name',number=1)[0].decode('utf-8')

                    t = pool.submit(user_detail, name)
                    t_list.append(t)
                except Exception as e:
                    logger.info("redis中user_name set 为空，程序结束！")
                    break
        else:
            logger.info("redis中user_name set 为空，程序结束！")
            break


