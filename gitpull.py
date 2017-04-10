#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author: hcylus
license: GPL
site: https://github.com/hcylus
file: gitpull.py
time: 2017/4/1 上午10:56
copyright: © DevOps

"""

from __future__ import unicode_literals

import sys

reload(sys)
sys.setdefaultencoding('utf8')

import os, subprocess, time
# try:
from urllib2 import urlopen

# except:
#     from urllib.request import urlopen


citime = time.strftime('%Y%m%d%H%m')

giturl = 'https://git.digi-sky.com/rs/crt_ses.git'
gitrepo = giturl.split('/')[-1].split('.')[0]
gitclone = 'git clone ' + giturl
gitfetch = 'git fetch --all'
gitreset = 'git reset --hard origin/master'
gitclean = 'git clean -df'
gitpull = 'git pull'
gitadd = 'git add *'
gitci = 'git commit -m' + '\'' + citime + ' update' + '\''

gitdir = os.path.join(os.getenv('HOME'), gitrepo)
svnurl = 'http://192.168.2.60:8080/svn/crt_all/'
cmdburl = 'http://192.168.20.250/ssh_session/update_svn'
svncmd = 'svn co ' + svnurl + ' ' + gitdir
svnup = 'svn update'


def cmdbupdate():
    try:
        response = urlopen(cmdburl, timeout=10)
        html = response.read()
        # print html
        if 'OK' not in html:
            print('由cmdb更新至svn失败')
            return False
        else:
            print('由cmdb更新至svn成功')
            return True
    except:
        print('访问更新cmdb到svn的url失败!')
        return False


def gitupdate():
    os.chdir(os.getenv('HOME'))
    if os.path.isdir(gitrepo):
        os.chdir(gitrepo)
        subprocess.check_call(gitclean, shell=True)
        subprocess.check_call(gitpull, shell=True)
        cmdbupdate()
        subprocess.check_call(svnup, shell=True)
    else:
        subprocess.check_call(gitclone, shell=True)
        cmdbupdate()
        subprocess.check_call(svncmd, shell=True)


def gitpush():
    os.chdir(gitdir)
    subprocess.check_call(gitfetch, shell=True)
    subprocess.check_call(gitreset, shell=True)
    subprocess.check_call(gitadd, shell=True)
    subprocess.check_call(gitci, shell=True)
    # subprocess.check_call('git push',shell=True)


gitupdate()
gitdir = os.path.join(os.getenv('HOME'), gitrepo)
gitpush()
