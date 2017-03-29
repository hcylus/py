#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author: hcylus
license: GPL
site: https://github.com/hcylus
file: mp.py
time: 2017/3/27 22:27
"""

from multiprocessing import Pool, Manager


def wq(q):
    for value in xrange(10):
        q.put(value)
        print "Put %s" % value
    print "Put over"


def rq(q):
    while 1:
        if not q.empty():
            value = q.get()
            print "Get %s" % value
        else:
            break
    print "Get over"


if __name__ == "__main__":
    q = Manager().Queue()
    p = Pool()
    wp = p.apply_async(wq, args=(q,))
    rp = p.apply_async(rq, args=(q,))
    p.close()
    p.join()
    print "Queue over"
