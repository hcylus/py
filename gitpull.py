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

# giturl = 'https://git.digi-sky.com/rs/crt_ses.git'
giturl = 'git@git.digi-sky.com:rs/crt_ses.git'
gitrepo = giturl.split('/')[-1].split('.')[0]
gitclone = 'git clone ' + giturl
gitfetch = 'git fetch --all'
gitreset = 'git reset --hard origin/master'
gitclean = 'git clean -df'
# gitpull = 'git pull'
gitadd = 'git add *'
gitci = 'git commit -m' + '\'' + citime + ' update' + '\''
gitdir = os.path.join(os.getenv('HOME'), gitrepo)

svndir = os.path.join(os.getenv('HOME'), 'crt_all/')
svnurl = 'http://192.168.2.60:8080/svn/crt_all/'
cmdburl = 'http://192.168.20.250/ssh_session/update_svn'
svncmd = 'svn co ' + svnurl + ' --username yw'
svnup = 'svn update'
svnclean = 'svn st | grep \'^?\' | awk \'{print $2}\' | xargs rm -rf'

rsyncmd = 'rsync -av --exclude \'.svn\' --exclude \'__FolderData__.ini\' ' + svndir + ' ' + gitdir

def cmdbupdate(func):
    def _cmdbupdate():
        try:
            response = urlopen(cmdburl, timeout=10)
            html = response.read()
            # print html
            if 'OK' not in html:
                print('由cmdb更新至svn失败')
                # return False
                func()
            else:
                print('由cmdb更新至svn成功')
                # return True
                func()
        except:
            print('访问更新cmdb到svn的url失败!')
            # return False
            func()
    return _cmdbupdate

@cmdbupdate
def svnupdate():
    os.chdir(os.getenv('HOME'))
    if os.path.isdir(svndir):
        os.chdir(svndir)
        subprocess.check_call(svnclean, shell=True)
        subprocess.check_call(svnup, shell=True)
    else:
        subprocess.check_call(svncmd, shell=True)

def gitupdate(func):
    def _gitupdate():
        os.chdir(os.getenv('HOME'))
        if os.path.isdir(gitrepo):
            os.chdir(gitrepo)
            subprocess.check_call(gitclean, shell=True)
            subprocess.check_call(gitfetch, shell=True)
            subprocess.check_call(gitreset, shell=True)
            func()
        else:
            subprocess.check_call(gitclone, shell=True)
            func()
    return _gitupdate

@gitupdate
def gitpush():
    os.chdir(os.getenv('HOME'))
    subprocess.check_call(rsyncmd, shell=True)
    os.chdir(gitdir)
    subprocess.check_call(gitadd, shell=True)
    subprocess.check_call(gitci, shell=True)
    subprocess.check_call('git push', shell=True)

svnupdate()
gitpush()
