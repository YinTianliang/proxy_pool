# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyManager.py  
   Description :  
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/3:
                   2018/4/22: 增加了代理的其它信息, get增加了参数
-------------------------------------------------
"""
__author__ = 'JHao'

import random

from Util import EnvUtil
from DB.DbClient import DbClient
from Util.GetConfig import GetConfig
from Util.LogHandler import LogHandler
from Util.utilFunction import verifyProxyFormat
from ProxyGetter.getFreeProxy import GetFreeProxy


class ProxyManager(object):
    """
    ProxyManager
    """

    def __init__(self):
        self.db = DbClient()
        self.config = GetConfig()
        self.raw_proxy_queue = 'raw_proxy'
        self.log = LogHandler('proxy_manager')
        self.useful_proxy_queue = 'useful_proxy'
        self.proxy_speed = 'proxy_speed'
        self.proxy_annoy = 'proxy_annoy'
        self.proxy_type = 'proxy_type'

    def refresh(self):
        """
        fetch proxy into Db by ProxyGetter
        :return:
        """
        for proxyGetter in self.config.proxy_getter_functions:
            # fetch
            proxy_set = set()
            try:
                self.log.info("{func}: fetch proxy start".format(func=proxyGetter))
                proxy_iter = [_ for _ in getattr(GetFreeProxy, proxyGetter.strip())()]
            except Exception as e:
                self.log.error("{func}: fetch proxy fail".format(func=proxyGetter))
                continue
            for proxy in proxy_iter:
                proxy = tuple(item.strip() for item in proxy)
                if proxy and verifyProxyFormat(proxy):
                    self.log.info('{func}: fetch proxy {proxy}'.format(func=proxyGetter, proxy=proxy))
                    proxy_set.add(proxy)
                else:
                    self.log.error('{func}: fetch proxy {proxy} error'.format(func=proxyGetter, proxy=proxy))

            # store
            for proxy in proxy_set:
                self.db.changeTable(self.useful_proxy_queue)
                if self.db.exists(proxy[0]):
                    continue
                self.db.changeTable(self.raw_proxy_queue)
                self.db.put(proxy[0])
                self.db.changeTable(self.proxy_annoy)
                self.db.put(proxy[0], num=proxy[1])
                self.db.changeTable(self.proxy_type)
                self.db.put(proxy[0], num=proxy[2].upper())

    def get(self, **kwargs):
        """
        return a useful proxy
        :param kwargs:
        :return:
        """
        def check(proxy):
            if kwargs['type'] and not (proxy['type'] == kwargs['type'] or kwargs['type'] == 'HTTP/HTTPS'):
                return False
            if kwargs['max_speed'] and not (float(proxy['speed']) < float(kwargs['max_speed'])):
                return False
            if kwargs['annoy'] and not (proxy['annoy'] in kwargs['annoy']):
                return False
            return True

        proxies = ProxyManager().getFull()

        if proxies:
            return random.choice([proxy['address'] for proxy in proxies if check(proxy)])
        return None

    def delete(self, proxy):
        """
        delete proxy from pool
        :param proxy:
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        self.db.delete(proxy)

    def getAll(self):
        """
        get all proxy from pool as list
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        item_dict = self.db.getAll()
        if EnvUtil.PY3:
            return list(item_dict.keys()) if item_dict else list()
        return item_dict.keys() if item_dict else list()

    def getFull(self):
        """
        get all proxy with full infomation from poll as list
        :return:
        """
        proxy_info = {
            self.useful_proxy_queue: 'address',
            self.proxy_annoy: 'annoy',
            self.proxy_type: 'type',
            self.proxy_speed: 'speed'
        }

        item_dict = {}

        for key, value in proxy_info.items():
            self.db.changeTable(key)
            item_dict[value] = self.db.getAll()

        item_list = []
        for addr in item_dict['address']:
            item = {item: item_dict[item][addr] for item in item_dict.keys()}
            item['address'] = addr
            item_list.append(item)

        return item_list

    def getNumber(self):
        self.db.changeTable(self.raw_proxy_queue)
        total_raw_proxy = self.db.getNumber()
        self.db.changeTable(self.useful_proxy_queue)
        total_useful_queue = self.db.getNumber()
        return {'raw_proxy': total_raw_proxy, 'useful_proxy': total_useful_queue}


if __name__ == '__main__':
    pp = ProxyManager()
    pp.refresh()
