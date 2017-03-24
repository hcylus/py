#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author: hcylus
license: GPL
site: https://github.com/hcylus
file: argparsex.py
time: 2017/3/24 下午5:17
copyright: © DevOps

"""

import argparse

# def argparser():
parser = argparse.ArgumentParser(description='simple parser commang-line')
parser.add_argument('-u', '--user', dest='user', metavar='root', action='store', type=str, help="user name")
parser.add_argument('-p', '--pass', dest='password', metavar='xxx', action='store', type=str, help="user password")
parser.add_argument('-P', '--port', dest='port', metavar='3306', type=int, default=3306, help="program port")
parser.add_argument('-d', '--databases', nargs='+', help="database name")
parser.add_argument('test', nargs='?', help="test args")
args = parser.parse_args()
# return args

# if "__name__" == "__main__":
#     argparser()
