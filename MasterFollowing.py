# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# # @Time    : 2019/1/15 17:26
# # @Author  : Sa.Song
# # @Desc    :
# # @File    : following.py
# # @Software: PyCharm
#
import configparser
import json
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import requests
from lxml import etree
from conn_redis import get_link
# from get_proxy import get_proxy
from test import get_proxy
from PublicLog import public_log
cf = configparser.ConfigParser()
cf.read('conf.ini')
headers = {
    'authority': 'www.zhihu.com',
    'method': 'GET',
    'scheme': 'https',
    'accept-encoding':'gzip, deflate, br',
    'cookie':'tgw_l7_route=7c109f36fa4ce25acb5a9cf43b0b6415; _xsrf=jKLOKeMr5B7ymogXnWMxzsTI8lovQ7AC; _zap=60785992-3dcd-4133-9d59-36e788a58a82; d_c0="ADAipPkdEw-PTvS2GlazM6BpPtmiDErV8MU=|1551760963"; q_c1=1c472d1aeb5145d9bf0b4eb9d20e9f47|1551760965000|1551760965000'
    ,'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
}
basic_url = 'https://www.zhihu.com/people/'
start_name = cf.get('start_name', 'start_name')
following = cf.get('module', 'following')
db_host = cf.get('db', 'db_host')
db_user = cf.get('db', 'db_user')
db_pass = cf.get('db', 'db_pass')
db_database = cf.get('db', 'db_database')
logger = public_log()
timeout = 60

def get_html(url):
    try:
        try:
            result = requests.get(url, headers=headers, timeout=timeout)
        except Exception as e:
            proxy = get_proxy()
            result = requests.get(url, headers=headers, proxies=proxy, timeout=timeout)
        if result.status_code != 200:  # 根据其返回值代码判断其是否成功请求到目标页面

            try:
                proxy = get_proxy()
                result = requests.get(url, headers=headers, proxies=proxy, timeout=timeout)
            except Exception as e:
                proxy = get_proxy()
                result = requests.get(url, headers=headers, proxies=proxy, timeout=timeout)
        html = etree.HTML(result.text)
        print(result.text)
        if html.xpath('//title/text()')[0] == '安全验证 - 知乎':
            print('验证码！')
            try:
                proxy = get_proxy()
                result = requests.get(url, headers=headers, proxies=proxy, timeout=timeout)
                html = etree.HTML(result.text)
            except Exception as e:
                proxy = get_proxy()
                result = requests.get(url, headers=headers, proxies=proxy, timeout=timeout)
                html = etree.HTML(result.text)
        print(result.text)
        return html
    except Exception as e:
        print('有异常')
        return 0



def get_page_num(module_num, user_name=start_name):  # 获取following的总页数
    """
    获取每个用户的following总页数
    :param session:
    :param module_num:
    :param user_name:
    :return:
    """
    first_url = basic_url + user_name + '/' + module_num
    html = get_html(first_url)
    if html != 0:
        try:
            page_button = html.xpath(
                '//div[@class="Pagination"]/button[contains(@class,"PaginationButton") and contains(@class," Button--plain")]')
            page_num = int(page_button[-2].xpath('.//text()')[0])  # 关注列表总页数
        except Exception as e:
            page_num = 0
        return page_num


def main_logic(url, user_name):
    num = 0
    html = get_html(url)
    if html != 0:
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
                        conn.sadd("TokenBefore", i)  # 将用户唯一id存入redis
                    except Exception as e:
                        logger.info("TokenBefore 入redis异常>>>"+str(e))
        except Exception as e:
            logger.info("获取用户token失败>>>" + str(e))


def user_detail(user_name=start_name):
    page_num = get_page_num(following, user_name)  # 获取总页数
    if page_num:
        for page in range(page_num):
            new_url = 'https://www.zhihu.com/people/{0}/{1}?page={2}'.format(user_name, following, str(page + 1))
            #  url拼接原理：原始路径 + username + 页面模块标识 + page
            main_logic(new_url, user_name)
    else:
        new_url = 'https://www.zhihu.com/people/{0}/{1}'.format(user_name, following)
        #  url拼接原理：原始路径 + username + 页面模块标识 + page
        main_logic(new_url, user_name)

def get_session():
    s = requests.Session()
    with open('session.txt', 'r', encoding='utf-8') as f:
        cookies = json.load(f)
        for cookie in cookies:
            requests.utils.add_dict_to_cookiejar(s.cookies, {cookie['name']: cookie['value']})
    return s

if __name__ == '__main__':
    t_list = []
    user_detail()
    pool = ThreadPoolExecutor(max_workers=8)
    while True:
        wait(t_list, return_when=ALL_COMPLETED)  # 等待子进程结束
        conn = get_link()
        if conn.scard('TokenAfter') <= conn.scard('TokenBefore'):
            for i in range(4):
                try:
                    name = conn.srandmember(name='TokenBefore', number=1)[0].decode('utf-8')
                    if not conn.sismember('TokenAfter', name):
                        t = pool.submit(user_detail, name)
                        conn.sadd("TokenAfter", name)
                        t_list.append(t)
                except Exception as e:
                    logger.error("可能会有异常>>>"+str(e))
                    break
        else:
            logger.info("TokenBefore set 中所有token全遍历过了，程序结束！")
            break
