#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author: hcylus
license: GPL
site: https://github.com/hcylus
file: crt.py
time: 2017/3/30 上午10:41
copyright: © DevOps

"""

from __future__ import unicode_literals

import os
import platform
import re
import subprocess
import sys
from multiprocessing import Pool, Value, Lock

try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except:
    pass
try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen

# 用户目录
if platform.system() == 'Windows':
    USER_HOME = os.environ.get('HOMEPATH')
else:
    USER_HOME = os.environ.get('HOME')
# 工作目录,sz,rz文件存放目录,sftp主目录
WORK_DIR = os.path.join(USER_HOME, 'work')
# 日志存放目录
LOG_DIR = os.path.join(USER_HOME, 'Session_log')
# SecureCrt的Config目录
CRT_CONF = os.path.join(USER_HOME, 'Library', 'Application Support', 'VanDyke', 'SecureCRT', 'Config')
# Session读取目录,一般是svn的目录
SESSION_SRC = os.path.join(USER_HOME, 'svn', 'crt_all')
# 是否在操作前执行svn更新操作
SVN_UPDATE = True
# 是否在更新svn前,从cmdb同步session到svn
CMDB_SVN_UPDATE = True
CMDB_SVN_URL = 'http://192.168.20.250/ssh_session/update_svn'
# Session输出存放目录,一般做个软链接到securecrt的session目录.
SESSION_DST = os.path.join(USER_HOME, 'crt', 'session')
# 是否启用自动登录脚本
SCRIPT_ENABLE = True
# 自动登录脚本存放位置
SCRIPT_FILE = os.path.join(USER_HOME, 'crt', 'login.py')
# 默认编码
LOCALE = 'UTF-8'
# 颜色主题
# Floral White / Dark Cyan 我喜欢的,在mpb下面显示不刺眼
# Traditional 黑底绿字,可能会喜欢
# White / Black 黑底白字
# Yellow / Black 黑底黄字
# Monochrome 默认的白底黑字
COLOR_SCHEME = 'Floral White / Dark Cyan'


# 终端类型,默认为Linux,另一个常用的为Xterm
def term_type(config_str, type='Linux'):
    s = config_str
    s = re.sub(r'(.*"ANSI Color".*)=(\d+)', r"\1=%08d" % True, s)
    s = re.sub(r'(.*"Emulation".*)=(.*)', r"\1=%s" % type, s)
    s = re.sub(r'(.*"Keymap Name".*)=(.*)', r"\1=%s" % type, s)
    return s


# 默认每隔60s,发送一个no-op空操作,防止ssh断线
def send_noop(config_str, timeout=60):
    s = config_str
    s = re.sub(r'(.*"Idle NO-OP Check".*)=(\d+)', r"\1=%08d" % True, s)
    s = re.sub(r'(.*"Idle NO-OP Timeout".*)=([0-9a-fA-F]+)', r"\1=%08x" % timeout, s)
    return s


# 设置默认编码为utf-8
def locale(config_str, type=LOCALE):
    s = config_str
    s = re.sub(r'(.*"Output Transformer Name".*)=(.*)', r"\1=%s" % type, s)
    s = re.sub(r'(.*"Use Unicode Line Drawing".*)=(\d+)', r"\1=%08d" % True, s)
    return s


# 颜色主题
# Floral White / Dark Cyan 我喜欢的,在mpb下面显示不刺眼
# Traditional 黑底绿字,可能会喜欢
# White / Black 黑底白字
# Yellow / Black 黑底黄字
# Monochrome 默认的白底黑字
def color_scheme(config_str, scheme=COLOR_SCHEME):
    s = config_str
    s = re.sub(r'(.*"Color Scheme Overrides Ansi Color".*)=(\d+)', r"\1=%08d" % True, s)
    s = re.sub(r'(.*"Color Scheme".*)=(.*)', r"\1=%s" % scheme, s)
    return s


# 字体设置
# 只针对macOS有效,windows/linux系统会忽略这个.
# 默认使用Menlo 14pt
def font(config_str):
    s = config_str
    if platform.system() == 'Darwin':
        s = re.sub(r'(.*"Normal Font v2".*)=([0-9a-fA-F\s]*\n*\n)',
                   r"\1=00000040\n" + \
                   " ee ff ff ff 09 00 00 00 00 00 00 00 00 00 00 00 f4 01 00 00 00 00 00 00 00 00 00 01 4d 65 6e 6c\n" + \
                   " 6f 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 8c 00 00 00\n",
                   s)
        s = re.sub(r'(.*"Normal Font v2".*)=([0-9a-fA-F\s]*\n*\n)',
                   r"\1=00000040\n" + \
                   " ee ff ff ff 09 00 00 00 00 00 00 00 00 00 00 00 f4 01 00 00 00 00 00 00 00 00 00 01 4d 65 6e 6c\n" + \
                   " 6f 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 8c 00 00 00\n",
                   s)
    return s


# 日志设置
# %S - seesion名字, %H - 主机名字, %M - 月, %D 日, %h - 小时, %m - 分钟
def log_fmt(config_str,
            filename=os.path.join(LOG_DIR, '%S%Y%M%D.log'),  # 日志名称,每个session按天命名
            connect=' ======开始于%Y年%M月%D日  %h时%m分====== ',  # 连接开始的提示
            disconnect=' ======结束于%Y年%M月%D日  %h时%m分====== ',  # 连接结束的提示
            line='%Y/%M/%D %h:%m',  # 每行开始的标记
            ):
    s = config_str
    s = re.sub(r'(.*"Log Mode".*)=(\d+)', r"\1=%08d" % True, s)  # 强制设置追加模式,避免老的日志被覆盖
    s = re.sub(r'(.*"Start Log Upon Connect".*)=(\d+)', r"\1=%08d" % True, s)  # 开始连接的时候就开始记录
    s = re.sub(r'(.*"New Log File At Midnight".*)=(\d+)', r"\1=%08d" % True, s)  # 午夜时候自动开始新的日志文件
    s = re.sub(r'(.*"Log Filename V2".*)=(.*)', r"\1=%s" % filename, s)
    s = re.sub(r'(.*"Log Filename".*)=(.*)', r"\1=%s" % filename, s)
    s = re.sub(r'(.*"Custom Log Message Connect")=(.*)', r"\1=%s" % connect, s)
    s = re.sub(r'(.*"Custom Log Message Disconnect")=(.*)', r"\1=%s" % disconnect, s)
    s = re.sub(r'(.*"Custom Log Message Each Line".*)=(.*)', r"\1=%s" % line, s)
    return s


# 用户目录设置
# sz,rz本地路径,sftp主目录
def user_dir(config_str):
    s = config_str
    s = re.sub(r'(.*"Sftp Tab Local Directory V2".*)=(.*)', r"\1=%s" % WORK_DIR, s)
    s = re.sub(r'(.*"Upload Directory V2".*)=(.*)', r"\1=%s" % WORK_DIR, s)
    s = re.sub(r'(.*"Download Directory V2".*)=(.*)', r"\1=%s" % WORK_DIR, s)
    s = re.sub(r'(.*"Sftp Tab Local Directory".*)=(.*)', r"\1=%s" % WORK_DIR, s)
    s = re.sub(r'(.*"Upload Directory".*)=(.*)', r"\1=%s" % WORK_DIR, s)
    s = re.sub(r'(.*"Download Directory".*)=(.*)', r"\1=%s" % WORK_DIR, s)
    return s


# 使用脚本进行登录
def script_enable(config_str):
    s = config_str
    if SCRIPT_ENABLE == False:
        return s
    s = re.sub(r'(.*"Auth Prompts in Window".*)=(\d+)', r"\1=%08d" % True, s)
    s = re.sub(r'(.*"Use Script File".*)=(\d+)', r"\1=%08d" % True, s)
    s = re.sub(r'(.*"Script Filename V2".*)=(.*)', r"\1=%s" % SCRIPT_FILE, s)
    s = re.sub(r'(.*"Script Filename".*)=(.*)', r"\1=%s" % SCRIPT_FILE, s)
    return s


def host_port(config_str, host, port):
    s = config_str
    s = re.sub(r'(.*"Hostname".*)=(.*)', r"\1=%s" % host, s)
    s = re.sub(r'(.*"\[SSH2\] Port".*)=([0-9a-fA-F]+)', r"\1=%s" % port, s)
    return s


def config_rules(config_str, host, port):
    s = config_str
    s = host_port(s, host, port)
    s = term_type(s)
    s = send_noop(s)
    s = locale(s)
    s = color_scheme(s)
    s = font(s)
    s = log_fmt(s)
    s = user_dir(s)
    s = script_enable(s)
    return s


def svn_update():
    print('svn 更新开始')
    old_path = os.getcwd()
    try:
        os.chdir(SESSION_SRC)
        print(SESSION_SRC)
        subprocess.check_call('svn cleanup', shell=True)
        subprocess.check_call('svn update', shell=True)
        print('svn 更新成功')
        os.chdir(old_path)
    except:
        print('svn 更新失败')
        os.chdir(old_path)


def cmdb_svn_update():
    try:
        response = urlopen(CMDB_SVN_URL, timeout=10)
        html = response.read()
        print(html)
        if 'OK' not in html:
            print('由cmdb更新至svn失败')
            return False
        else:
            print('由cmdb更新至svn成功')
            return True
    except:
        print('访问更新cmdb到svn的url失败!')
        return False


def config_edit(session):
    global s_num
    global session_src_l_sum
    global lock
    global val
    global default_conf
    src_f = open(session, 'r')
    src_str = src_f.read()
    src_f.close()
    try:
        hostname = re.search(r'(.*"Hostname".*)=(.*)', src_str).group(2)
        port = re.search(r'(.*"\[SSH2\] Port".*)=(.*)', src_str).group(2)
    except:
        print(session)
        print('hostname,port没有在文件中匹配到.')
        sys.stdout.flush()
        exit(3)
    config_str = config_rules(default_conf, hostname, port)
    session_dst = SESSION_DST + session.split(SESSION_SRC)[1]
    session_dst_path = os.path.split(session_dst)[0]
    os.path.isdir(session_dst_path) or os.makedirs(session_dst_path)
    if not os.path.isdir(session_dst_path):
        print(session_dst_path)
        print('session 输出目录不存在 或者无法创建')
        exit(3)
    dst_f = open(session_dst, 'w')
    dst_f.write(config_str)
    dst_f.close()
    lock.acquire()
    val.value += 1
    msg = '正在处理session  (%d|%d)\r' % (val.value, session_src_l_sum)
    sys.stdout.write(msg)
    sys.stdout.flush()
    lock.release()


def __init_lock(l, v):
    global lock
    global val
    lock = l
    val = v


def main():
    if not os.path.isdir(SESSION_SRC):
        print('src|svn 目录不存在, 请把session的svn本地目录地址赋值给SESSION_SRC')
        exit(3)
    if not os.path.isdir(CRT_CONF):
        print('SecureCRT的config目录不正确,重新赋值CRT_CONF!')
        exit(3)
    crt_session_dir = os.path.join(CRT_CONF, 'Sessions')
    if os.path.isfile(os.path.join(crt_session_dir, 'Default.ini')):
        default_ini_f = os.path.join(crt_session_dir, 'Default.ini')
    elif os.path.isfile(os.path.join(crt_session_dir, 'default.ini')):
        default_ini_f = os.path.join(crt_session_dir, 'default.ini')
    else:
        print('SecureCRT的默认模板Default.ini|default.ini不存在,检查CRT_CONF的设置')
        exit(3)
    os.path.isdir(SESSION_DST) or os.makedirs(SESSION_DST)
    if not os.path.isdir(SESSION_DST):
        print(SESSION_DST)
        print('session 输出目录不存在 或者无法创建')
        exit(3)
    if SVN_UPDATE == True:
        if CMDB_SVN_UPDATE == True:
            cmdb_svn_update()
        svn_update()
    session_src_l = []
    for p in os.walk(SESSION_SRC):
        if p[2] != []:
            for f in p[2]:
                if '.ini' not in f:
                    continue
                if f in ["Default.ini", "__FolderData__.ini"]:
                    continue
                f_path = os.path.join(p[0], f)
                if f_path not in session_src_l:
                    session_src_l.append(os.path.join(p[0], f))
    session_dst_l = []
    for p in os.walk(SESSION_DST):
        if p[2] != []:
            for f in p[2]:
                if '.ini' not in f:
                    continue
                if f in ["Default.ini", "__FolderData__.ini"]:
                    continue
                f_path = os.path.join(p[0], f)
                if f_path not in session_dst_l:
                    session_dst_l.append(os.path.join(p[0], f))
    session_dst_rm_l = []
    for session in session_dst_l:
        if SESSION_SRC + session.split(SESSION_DST)[1] not in session_src_l:
            session_dst_rm_l.append(session)
    session_dst_rm_sum = len(session_dst_rm_l)
    num = 0
    msg = '\n正在删除多余的session  (%d|%d)\r' % (num, session_dst_rm_sum)
    sys.stdout.write(msg)
    sys.stdout.flush()
    for session_dst_rm in session_dst_rm_l:
        os.remove(session_dst_rm)
        num = num + 1
        msg = '正在删除多余的session  (%d|%d)\r' % (num, session_dst_rm_sum)
        sys.stdout.write(msg)
        sys.stdout.flush()
    global session_src_l_sum
    session_src_l_sum = len(session_src_l)
    global default_conf
    default_ini = open(default_ini_f, 'r')
    default_conf = default_ini.read()
    default_ini.close()
    msg = '\n正在处理session  (%d|%d)\r' % (0, session_src_l_sum)
    sys.stdout.write(msg)
    sys.stdout.flush()
    v = Value('i', 0)
    l = Lock()
    pool = Pool(initializer=__init_lock, initargs=(l, v,))
    pool.map_async(config_edit, session_src_l).get(2000)
    sys.stdout.write('\n')
    exit(0)


if __name__ == "__main__":
    main()
