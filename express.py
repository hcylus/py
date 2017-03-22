# -*- coding: utf-8 -*-
import sys, urllib, urllib2, json

url1 = 'http://apis.baidu.com/netpopo/express/express2'

req1 = urllib2.Request(url1)

req1.add_header("apikey", "a136df923c709e7b8c1b436a78816f59")

resp = urllib2.urlopen(req1)
content = resp.read()
if (content):
    print(content)

url2 = 'http://apis.baidu.com/netpopo/express/express1?type=EMS&number=1022411009918'

req2 = urllib2.Request(url2)

req2.add_header("apikey", "a136df923c709e7b8c1b436a78816f59")

resp = urllib2.urlopen(req2)
content = resp.read()
if (content):
    print(content)
