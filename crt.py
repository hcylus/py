#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
author: hcylus
license: GPL
site: https://github.com/hcylus
file: crt.py
time: 2017/3/31 下午4:24
copyright: © DevOps

'''

from __future__ import unicode_literals

'''
描述：脚本主要用于处理SecureCrt会话文件，从而解决重复手动修改每个会话配置
处理逻辑：
1.带参数运行：参数用于设置会话保存目录（可从软件全局选项里找到路径，将此路径赋值于变量），生成或更新变量保存文件（默认用户目录下.crtconfig文件）
2.不带参数运行：
a.采用SecureCrt默认会话保存目录（按默认配置生成crtcnf文件）
b.已存在crtconf文件（会话目录设置未修改过情况），使用crtconf文件参数
依赖：所有会话文件生成都依赖全局默认Default.ini会话文件
目的：使用用户偏好设置，减少脚本硬编程，跨版本、跨平台，无需太多依赖
'''

import os, sys, time
import argparse
import platform, subprocess
import re
from multiprocessing import Pool, Manager, freeze_support
from ConfigParser import ConfigParser

start = time.time()

# git相关变量设置
giturl = 'https://git.digi-sky.com/rs/crt_ses.git'
gitrepo = giturl.split('/')[-1].split('.')[0]
gitclone = 'git clone ' + giturl
gitfetch = 'git fetch --all'
gitreset = 'git reset --hard origin/master'
gitclean = 'git clean -df'

# 匹配ini文件里主机ip
host = re.compile(
    r'(.*"Hostname"=)((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))\n')
host_pre = re.compile(r'.*"Hostname"=')

# 操作系统版本判断，并获取默认session存放路径
global user_profile, crt_defcnfdir, crt_cnfdir
if platform.system() == 'Darwin':
    user_profile = os.getenv('HOME')
    crt_defcnfdir = os.path.join(user_profile, 'Library', 'Application Support', 'VanDyke', 'SecureCRT', 'Config')
elif platform.system() == 'Windows':
    user_profile = os.getenv('USERPROFILE')
    user_appdata = os.getenv('APPDATA')
    crt_defcnfdir = os.path.join(user_appdata, 'VanDyke', 'Config')

# 通过判断脚本是否带参来更新默认session存放路径
parser = argparse.ArgumentParser(description='configuration session path')
parser.add_argument('-u', '--update', dest='sessiondir', metavar='path', action='store', type=str,
                    help='set session path')

# 更新session存放路径
parserargs = parser.parse_args()
crt_cnf = os.path.join(user_profile, '.crtcnf')
cf = ConfigParser()

if not parserargs.sessiondir:
    if not os.path.exists(crt_cnf):
        crt_cnfdir = crt_defcnfdir
        cf.add_section('global')
        cf.set('global', 'cnfdir', crt_cnfdir)
        cf.write(open(crt_cnf, 'w+'))
    else:
        cf.read(crt_cnf)
else:
    crt_cnfdir = parserargs.sessiondir
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
# except (OSError, WindowsError) as e:
except OSError as e:
    print(e)
    print('session path %s set error ,please check !!!' % crt_cnfdir)
    sys.exit(1)

def putsession(q):
    if os.path.exists(os.path.join(sessiondir, gitrepo)):
        try:
            os.chdir(os.path.join(sessiondir, gitrepo))
            subprocess.check_call(gitclean, shell=True)
            subprocess.check_call(gitfetch, shell=True)
            subprocess.check_call(gitreset, shell=True)
        except subprocess.CalledProcessError as e:
            print(e)
            print('git command not found or %s unable to access' % giturl)
            sys.exit(1)
    else:
        try:
            subprocess.check_call(gitclone, shell=True)
        except subprocess.CalledProcessError as e:
            print(e)
            print('git command not found or %s unable to access' % giturl)
            sys.exit(1)

    for dirpath, dirnames, filenames in os.walk(os.path.join(sessiondir, gitrepo)):
        for fname in filenames:
            if os.path.splitext(fname)[1] == '.ini':
                if fname != '__FolderData__.ini':
                    q.put(os.path.join(dirpath, fname))

def getsession(q):
    num = q.qsize()
    unmatch_host = []
    '''
    处理不同操作系统换行符问题
    python2 (可用os.linesep获取操作系统换行符)
    1）如果不是txt文件，建议用wb和rb来读写。通过二进制读写，不会有换行问题。
    2）如果需要明文内容，请用rU来读取（强烈推荐），即U通用换行模式（Universal new line mode）。该模式会把所有的换行符（\r \n \r\n）替换为\n。只支持读入

    Python3
    可以通过open函数的newline参数来控制Universal new line mode：
    读取时候，不指定newline，则默认开启Universal new line mode，所有\n, \r, or \r\n被默认转换为\n ；
    写入时，不指定newline，则换行符为各系统默认的换行符（\n, \r, or \r\n, ），指定为newline='\n'，则都替换为\n（相当于Universal new line mode）；
    不论读或者写时，newline=''都表示不转换。

    '''
    with open(os.path.join(sessiondir, 'Default.ini'), 'rU') as sestemplate:
        sestempini = sestemplate.read()
        while 1:
            if not q.empty():
                value = q.get()
                with open(value, 'rU') as sourceini:
                    try:
                        hostip = host.search(sourceini.read()).group()
                    except AttributeError as e:
                        unmatch_host.append(value)
                    else:
                        hostip = hostip.replace('\n', '')
                        tmpini = re.sub(host_pre, hostip, sestempini)
                        destini = open(value, 'w')
                        destini.write(tmpini)
                        destini.close()
            else:
                break

    len_unhost = len(unmatch_host)
    if unmatch_host:
        for unhost in unmatch_host:
            print(unhost)
        print('Unformat session nums: %d\nPlease check Unformat files' % len_unhost)

    print 'Format session nums: {}'.format(num - len_unhost)

if __name__ == "__main__":
    # 此处的freeze_support用于解决Windows下多进程异常问题
    freeze_support()
    # 定义队列，将session文件存入队列，以便进程池获取
    q = Manager().Queue()
    # 定义进程池
    p = Pool()
    # 队列写入使用单进程，以防重复写入数据
    putsession(q)
    # wp = p.apply_async(putsession, args=(q,))
    rp = p.apply_async(getsession, args=(q,))
    # getsession(q)
    p.close()
    p.join()
    end = time.time()
    print 'Cost Time:', format(end - start, '<10.2f')
