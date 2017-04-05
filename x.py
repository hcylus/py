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

import os, time
import platform, subprocess
from ConfigParser import ConfigParser
# from multiprocessing import Pool,Manager
from multiprocessing import Pool, Manager

giturl = 'https://github.com/hcylus/crt.git'
gitrepo = giturl.split('/')[-1].split('.')[0]
gitclone = 'git clone ' + giturl
gitfetch = 'git fetch --all'
gitreset = 'git reset --hard origin/master'
gitclean = 'git clean -df'
gitpull = 'git pull'

if platform.system() == 'Darwin':
    user_profile = os.getenv('HOME')
    # crt_defcnfdir = os.path.join(user_profile, 'Library', 'Application Support', 'VanDyke', 'SecureCRT', 'Config')
    crt_defcnfdir = os.path.join(user_profile, 'tx')
elif platform.system() == 'Windows':
    user_profile = os.getenv('USERPROFILE')
    user_appdata = os.getenv('APPDATA')
    crt_defcnfdir = os.path.join(user_appdata, 'VanDyke', 'Config')

## 通过sys.argv参数是否存在判断使用默认配置还是新配置
crt_cnfdir = crt_defcnfdir
crt_cnf = os.path.join(user_profile, '.crtcnf')

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
os.chdir(sessiondir)


def putsession(q):
    if os.path.exists(os.path.join(sessiondir, gitrepo)):
        os.chdir(os.path.join(sessiondir, gitrepo))
        print 'clean local files and pull files from git'
        # subprocess.check_call(gitclean, shell=True)
        # subprocess.check_call(gitfetch, shell=True)
        # subprocess.check_call(gitreset, shell=True)
        # subprocess.check_call(gitpull, shell=True)
    else:
        subprocess.check_call(gitclone, shell=True)

    for dirpath, dirnames, filenames in os.walk(os.path.join(sessiondir, gitrepo)):
        for fname in filenames:
            if os.path.splitext(fname)[1] == '.ini':
                if fname != '__FolderData__.ini':
                    q.put(os.path.join(dirpath, fname))


def getsession(q):
    print q.qsize()
    while 1:
        if not q.empty():
            values = q.get()
            print values
        else:
            break


if __name__ == "__main__":
    q = Manager().Queue()
    p = Pool()
    putsession(q)
    start = time.time()
    # wp = p.apply_async(putsession, args=(q,))
    rp = p.apply_async(getsession, args=(q,))
    # getsession(q)
    p.close()
    p.join()
    end = time.time()
    print 'COST: {}'.format(end - start)
