#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author: hcylus
license: GPL
site: https://github.com/hcylus
file: optparsex.py
time: 2017/3/22 22:20
"""

import sys
from optparse import OptionParser,OptionGroup

usage='"usage:%prog [options] arg1,arg2",version="%prog 1.0"'
#初始化对象
parse=OptionParser(usage)
parse.add_option('-u','--user',dest='user',action='store',type=str,metavar='user',help='enter user name')
parse.add_option('-p','--port',dest='port',action='store',type=int,metavar='xxx',default='3306',help='enter int port')
parse.add_option('-v','--version',metavar='1',help='version number')
#-u,--user 表示一个是短选项 一个是长选项
#dest='user' 将该用户输入的参数保存到变量user中，可以通过options.user方式来获取该值
#type=str，表示这个参数值的类型必须是str字符型，如果是其他类型那么将强制转换为str（可能会报错）
#metavar='user'，当用户查看帮助信息，如果metavar没有设值，那么显示的帮助信息的参数后面默认带上dest所定义的变量名
#help='Enter..',显示的帮助提示信息
#default=3306，表示如果参数后面没有跟值，那么将默认为变量default的值
parse.set_defaults(v=1.2)  #也可以这样设置默认值

#如果程序有很多的命令行参数，你可能想为他们进行分组，这时可以使用 OptionGroup
group = OptionGroup(parse, "Dangerous Options",
                    "Caution: use these options at your own risk.  "
                    "It is believed that some of them bite.")
group.add_option("-g","--group", action="store_true", help="Group option.")
parse.add_option_group(group)

options, args = parse.parse_args()
print 'OPTIONS:', options
print 'ARGS:', args

print '~' * 20
print 'user:', options.user
print 'port:', options.port
print 'version:', options.v

