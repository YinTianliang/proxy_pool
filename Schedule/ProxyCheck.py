# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyCheck
   Description :   多线程验证useful_proxy
   Author :        J_hao
   date：          2017/9/26
-------------------------------------------------
   Change Activity:
                   2017/9/26: 多线程验证useful_proxy
                   2018/4/22: 增加proxy_speed
-------------------------------------------------
"""
__author__ = 'J_hao'

import json
import sys
from threading import Thread

sys.path.append('../')

from Util.utilFunction import validUsefulProxy
from Manager.ProxyManager import ProxyManager
from Util.LogHandler import LogHandler

FAIL_COUNT = 1  # 校验失败次数， 超过次数删除代理


class ProxyCheck(ProxyManager, Thread):
    def __init__(self, queue, item_dict):
        ProxyManager.__init__(self)
        Thread.__init__(self)
        self.log = LogHandler('proxy_check', file=False)  # 多线程同时写一个日志文件会有问题
        self.queue = queue
        self.item_dict = item_dict

    def run(self):
        self.db.changeTable(self.useful_proxy_queue)
        while self.queue.qsize():
            proxy = self.queue.get()
            count = self.item_dict[proxy]
            speed = validUsefulProxy(proxy)
            if speed:
                # 验证通过计数器减1
                if count and int(count) > 0:
                    self.db.put(proxy, num=int(count) - 1)
                    self.db.changeTable(self.proxy_speed)
                    self.db.put(proxy, num=speed)
                    self.db.changeTable(self.useful_proxy_queue)
                else:
                    pass
                self.log.info('ProxyCheck: {} validation pass.[{:.3f}s]'.format(proxy, speed))
            else:
                self.log.info('ProxyCheck: {} validation fail'.format(proxy))
                if count and int(count) + 1 >= FAIL_COUNT:
                    self.log.info('ProxyCheck: {} fail too many, delete!'.format(proxy))
                    self.db.delete(proxy)
                    self.db.changeTable(self.proxy_speed)
                    self.db.delete(proxy)
                    self.db.changeTable(self.useful_proxy_queue)
                else:
                    self.db.put(proxy, num=int(count) + 1)
            self.queue.task_done()


if __name__ == '__main__':
    # p = ProxyCheck()
    # p.run()
    pass
