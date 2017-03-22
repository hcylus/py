#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author: hcylus
license: GPL
site: https://github.com/hcylus
file: getoptx.py
time: 2017/3/21 20:53
"""

import sys, getopt


def usage():
    """
    The docker-compose.yml initialization

Usage: getoptx.py [-n|--name,[projectname]] [-i|--input,[docker-compose.mako]] [-h|--help] [-o|--output],[docker-compose.yml]]

Description
            -n,--name django project name
            -i,--input  dockerfile mako template file
            -h,--help    Display help information.
            -o,--output  genarate .django docker-compose.yml file
for example:
    python getoptx.py -n dev -i docker-compose.mako -o docker-compose.yml
    """

#模糊匹配（参数为--h也能匹配为--help）
def getoptvalue():
    try:
        options, args = getopt.getopt(sys.argv[1:], "n:i:o:h", ["name=", "input=", "output=", "help"])
        print("options: "+str(options))
        print("args: "+str(args))
    except getopt.GetoptError as err:
        print(str(err))
        print(usage.__doc__)
        sys.exit(1)

    for k, v in options:
        print('key= '+k)
        print('value= '+v)

    # for arg in args:
    #     print('args= '+arg)
        if k in ('-n','--name'):
            print('projectname is '+v)
        elif k in ('-i','--input'):
            print('input file is '+v)
        elif k in ('-o','--output'):
            print('output file is '+v)
        elif k in ('-h', '--help'):
            print(usage.__doc__)
        else:
            print('syntax error')

if __name__ == "__main__":
    getoptvalue()
