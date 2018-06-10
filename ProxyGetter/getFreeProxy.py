# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     GetFreeProxy.py
   Description :  抓取免费代理
   Author :       JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25:
-------------------------------------------------
"""
import re
import sys
import requests

try:
    from importlib import reload  # py3 实际不会实用，只是为了不显示语法错误
except:
    reload(sys)
    sys.setdefaultencoding('utf-8')

sys.path.append('../')

from Util.utilFunction import robustCrawl, getHtmlTree
from Util.WebRequest import WebRequest

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()

"""
    66ip.cn
    data5u.com
    ip181.com
    xicidaili.com
    goubanjia.com
    xdaili.cn
    kuaidaili.com
    cn-proxy.com
    proxy-list.org
    www.mimiip.com
"""


class GetFreeProxy(object):
    """
    proxy getter
    """

    def __init__(self):
        pass

    @staticmethod
    def freeProxyFirst(page=10):
        """
        抓取无忧代理 http://www.data5u.com/
        :param page: 页数
        :return:
        """
        url_list = ['http://www.data5u.com/',
                    'http://www.data5u.com/free/',
                    'http://www.data5u.com/free/gngn/index.shtml',
                    'http://www.data5u.com/free/gnpt/index.shtml']
        for url in url_list:
            html_tree = getHtmlTree(url)
            ul_list = html_tree.xpath('//ul[@class="l2"]')
            for ul in ul_list:
                try:
                    yield [':'.join(ul.xpath('.//li/text()')[0:2])] +  ul.xpath('.//a/text()')[0:2]
                except Exception as e:
                    pass

    @staticmethod
    def freeProxySecond(proxy_number=100):
        """
        抓取代理66 http://www.66ip.cn/
        :param proxy_number: 代理数量
        :return:
        """
        url = "http://www.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=".format(
            proxy_number)
        request = WebRequest()
        html = request.get(url).text
        for proxy in re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html):
            yield [proxy, '透明', 'http']

    @staticmethod
    def freeProxyThird(days=1):
        """
        抓取ip181 http://www.ip181.com/
        :param days:
        :return:
        """
        url = 'http://www.ip181.com/'
        html_tree = getHtmlTree(url)
        try:
            tr_list = html_tree.xpath('//tr')[1:]
            for tr in tr_list:
                yield ':'.join(tr.xpath('./td/text()')[0:2])
        except Exception as e:
            pass

    @staticmethod
    def freeProxyFourth():
        """
        抓取西刺代理 http://api.xicidaili.com/free2016.txt
        :return:
        """
        url_list = ['http://www.xicidaili.com/nn',  # 高匿
                    'http://www.xicidaili.com/nt',  # 透明
                    ]
        for each_url in url_list:
            tree = getHtmlTree(each_url)
            proxy_list = tree.xpath('.//table[@id="ip_list"]//tr')[1:]
            for proxy in proxy_list:
                try:
                    info = proxy.xpath('./td[position() <= 3 or position() >= 5]/text()')
                    yield [':'.join(info[0:2])] + info[2:4]
                except Exception as e:
                    pass

    @staticmethod
    def freeProxyFifth():
        """
        抓取guobanjia http://www.goubanjia.com/
        :return:
        """
        url = "http://www.goubanjia.com/"
        tree = getHtmlTree(url)
        proxy_list = tree.xpath('//tbody/tr')
        # 此网站有隐藏的数字干扰，或抓取到多余的数字或.符号
        # 需要过滤掉<p style="display:none;">的内容
        xpath_str = """./td[@class="ip"]/*[not(contains(@style, 'display: none'))
                                        and not(contains(@style, 'display:none'))
                                        and not(contains(@class, 'port'))
                                        ]/text()
                                """
        for each_proxy in proxy_list:
            try:
                # :符号裸放在td下，其他放在div span p中，先分割找出ip，再找port
                ip_addr = ''.join(each_proxy.xpath(xpath_str))
                ip_type = each_proxy.xpath('./td/a/text()')[0:2]
                port = each_proxy.xpath(".//span[contains(@class, 'port')]/text()")[0]
                yield ['{}:{}'.format(ip_addr, port)] + ip_type
            except Exception as e:
                pass

    @staticmethod
    def freeProxySixth():
        """
        抓取讯代理免费proxy http://www.xdaili.cn/ipagent/freeip/getFreeIps?page=1&rows=10
        :return:
        """
        url = 'http://www.xdaili.cn/ipagent/freeip/getFreeIps?page=1&rows=10'
        request = WebRequest()
        try:
            res = request.get(url).json()
            for row in res['RESULT']['rows']:
                yield ['{}:{}'.format(row['ip'], row['port']), row['anony'], row['type']]
        except Exception as e:
            pass

    @staticmethod
    def freeProxySeventh():
        """
        快代理免费https://www.kuaidaili.com/free/inha/1/
        """
        url_list = [
            'https://www.kuaidaili.com/free/inha/{page}/',
            'https://www.kuaidaili.com/free/intr/{page}'
        ]

        for url in url_list:
            for page in range(1, 10):
                page_url = url.format(page=page)
                tree = getHtmlTree(page_url)
                proxy_list = tree.xpath('.//table//tr')[1:]
                for tr in proxy_list:
                    info = tr.xpath('./td/text()')
                    if info[2] == '高匿名':
                        info[2] = '高匿'
                    yield [':'.join(info[0:2])] + info[2:4]

    @staticmethod
    def freeProxyEight():
        """
        秘密代理IP网站http://www.mimiip.com
        """
        url_gngao = ['http://www.mimiip.com/gngao/%s' % n for n in range(1, 5)]  # 国内高匿
        url_gnpu = ['http://www.mimiip.com/gnpu/%s' % n for n in range(1, 5)]  # 国内普匿
        url_gntou = ['http://www.mimiip.com/gntou/%s' % n for n in range(1, 5)]  # 国内透明
        url_list = url_gngao + url_gnpu + url_gntou

        for url in url_list:
            tree = getHtmlTree(url)
            proxy_list = tree.xpath('//table[@class="list"]/tr')[1:]
            for proxy in proxy_list:
                info = proxy.xpath('./td/text()')
                ip_addr = ':'.join(info[0:2])
                yield [ip_addr] + info[5:7]

    @staticmethod
    def freeProxyNinth():
        """
        云代理,360三维代理(两网站长一样)
        http://www.ip3366.net/
        http://www.swei360.com/
        :return:
        """
        url_list = ['http://www.ip3366.net/?stype=1&page={}'.format(i) for i in range(1, 5)] + \
                   ['http://www.swei360.com/?page={}'.format(i) for i in range(1, 5)]

        for url in url_list:
            tree = getHtmlTree(url)
            proxy_list = tree.xpath('//div[@id="list"]//tr')[1:]
            for proxy in proxy_list:
                info = proxy.xpath('./td/text()')
                ip_addr = ':'.join(info[0:2])
                ip_annoy = info[2][0:2]
                if ip_annoy == '普通':
                    ip_annoy = '匿名'
                yield [ip_addr, ip_annoy, info[3]]

    @staticmethod
    def freeProxyWallFirst():
        """
        墙外网站 cn-proxy
        :return:
        """
        urls = ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218']
        request = WebRequest()
        for url in urls:
            r = request.get(url)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield [':'.join(proxy), '透明', 'HTTP']

    @staticmethod
    def freeProxyWallSecond():
        """
        墙外网站 proxy-list
        :return:
        """
        urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
        eng2chi = {
            'Transparent': '透明',
            'Anonymous': '匿名',
            'Elite': '高匿'
        }
        # request = WebRequest()
        import base64
        for url in urls:
            tree = getHtmlTree(url)
            proxy_list = tree.xpath('//div[@class="proxy-table"]//ul')
            for proxy in proxy_list[1:]:
                info = proxy.xpath('./li//text()')
                ip_addr = base64.b64decode(info[0].split("'")[1]).decode()
                yield [ip_addr, eng2chi[info[3]], info[1]]

    @staticmethod
    def xdaili():
        url = 'http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=f9e32b96fcb74629a7754c514f966e24&orderno=MF201861086776n9tsg&returnType=2&count=20'
        res = requests.get(url).json()

        if res['ERRORCODE'] == '0':
            for proxy in res['RESULT']:
                yield [proxy, '匿名', 'HTTP/HTTPS']


if __name__ == '__main__':
    gg = GetFreeProxy()
    # for e in gg.freeProxyFirst():
    #     print(e)
    #
    # for e in gg.freeProxySecond():
    #     print(e)
    #
    # for e in gg.freeProxyThird():
    #     print(e)
    #
    # for e in gg.freeProxyFourth():
    #     print(e)
    #
    # for e in gg.freeProxyFifth():
    #     print(e)
    #
    # for e in gg.freeProxySixth():
    #     print(e)
    #
    # for e in gg.freeProxySeventh():
    #     print(e)
    #
    # for e in gg.freeProxyEight():
    #     print(e)
    #
    # for e in gg.freeProxyWallFirst():
    #     print(e)
    #
    # for e in gg.freeProxyWallSecond():
    #     print(e)
