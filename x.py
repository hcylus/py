#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
author: hcylus
license: GPL
site: https://github.com/hcylus
file: x.py
time: 2017/3/31 下午4:24
copyright: © DevOps

'''

from __future__ import unicode_literals

'''
描述：脚本主要用于处理SecureCrt会话文件，已解决重复手动修改每个会话配置
处理逻辑：
1.带参数运行：参数用于设置全局会话保持目录（可从软件全局选项里找到路径，将此路径赋值于变量），生成或更新变量保存文件（默认用户目录.crtconfig）
2.不带参数运行：
a.脚本里硬编程SecureCrt默认全局会话保存目录（按默认配置生成crtcnf）
b.已存在.crtconf文件（全局会话目录设置未修改过情况）使用配置文件参数进行设置
依赖：所有会话文件生成都依赖全局默认会话文件
目的：最大化使用用户偏好本地设置，减少脚本硬编程，灵活迁移，无需太多依赖
'''

import os, sys
import argparse
import platform, subprocess
import re
from multiprocessing import Pool, Manager
from ConfigParser import ConfigParser

# 定义队列，将session文件存入队列，以便进程池获取
q = Manager().Queue()

# git相关变量设置
giturl = 'https://git.digi-sky.com/rs/crt_ses.git'
gitrepo = giturl.split('/')[-1].split('.')[0]
gitclone = 'git clone ' + giturl
gitfetch = 'git fetch --all'
gitreset = 'git reset --hard origin/master'
gitclean = 'git clean -df'

# 匹配ini文件里主机ip
host = re.compile(
    r'(.*"Hostname"=)((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))')
host_pre = re.compile(r'.*"Hostname"=')

# 操作系统版本判断，并获取默认session存放路径
if platform.system() == 'Darwin':
    user_profile = os.getenv('HOME')
    # crt_defcnfdir = os.path.join(user_profile, 'Library', 'Application Support', 'VanDyke', 'SecureCRT', 'Config')
    crt_defcnfdir = os.path.join(user_profile, 'tx')
elif platform.system() == 'Windows':
    user_profile = os.getenv('USERPROFILE')
    user_appdata = os.getenv('APPDATA')
    crt_defcnfdir = os.path.join(user_appdata, 'VanDyke', 'Config')

# 通过判断脚本是否带参来更新默认session存放路径
parser = argparse.ArgumentParser(description='configuration session path')
parser.add_argument('-u', '--update', dest='sessiondir', metavar='path', action='store', type=str,
                    help='set session path', default=crt_defcnfdir)
parserargs = parser.parse_args()
crt_cnfdir = parserargs.sessiondir
print crt_cnfdir
crt_cnf = os.path.join(user_profile, '.crtcnf')

# 更新session存放路径
cf = ConfigParser()
if not os.path.exists(crt_cnf):
    cf.add_section('global')
    cf.set('global', 'cnfdir', crt_cnfdir)
    cf.write(open(crt_cnf, 'w+'))
else:
    cf.read(crt_cnf)
    cf.set('global', 'cnfdir', crt_cnfdir)
    cf.write(open(crt_cnf, 'w+'))

s = cf.get('global', 'cnfdir')
sessiondir = os.path.join(s, 'Sessions')

try:
    os.chdir(sessiondir)
except OSError, e:
    print e
    print 'set session path error !!!'
    sys.exit(1)

def putsession(q):
    if os.path.exists(os.path.join(sessiondir, gitrepo)):
        try:
            os.chdir(os.path.join(sessiondir, gitrepo))
            subprocess.check_call(gitclean, shell=True)
            subprocess.check_call(gitfetch, shell=True)
            subprocess.check_call(gitreset, shell=True)
        # except subprocess.CalledProcessError, e:
        except:
            # print e
            # print 'install git'
            sys.exit(1)
    else:
        try:
            subprocess.check_call(gitclone, shell=True)
        except subprocess.CalledProcessError, e:
            print e
            sys.exit(1)

    for dirpath, dirnames, filenames in os.walk(os.path.join(sessiondir, gitrepo)):
        for fname in filenames:
            if os.path.splitext(fname)[1] == '.ini':
                if fname != '__FolderData__.ini':
                    q.put(os.path.join(dirpath, fname))

def getsession(q):
    num = q.qsize()
    with open(os.path.join(sessiondir, 'Default.ini'), 'r') as sestemplate:
        while 1:
            if not q.empty():
                value = q.get()
                with open(value, 'r') as sourceini:
                    hostip = host.search(sourceini.read()).group()
                    tmpini = re.sub(host_pre, hostip, sestemplate.read())
                    destini = open(value, 'w')
                    destini.write(tmpini)
                    destini.close()
            else:
                break

        print 'format session nums: ', num


if __name__ == "__main__":
    # 定义进程池
    p = Pool()
    putsession(q)
    # 队列写入使用单进程
    # wp = p.apply_async(putsession, args=(q,))
    rp = p.apply_async(getsession, args=(q,))
    p.close()
    p.join()
