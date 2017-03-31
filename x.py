#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author: hcylus
license: GPL
site: https://github.com/hcylus
file: x.py
time: 2017/3/31 下午4:24
copyright: © DevOps

"""

"""
描述：脚本主要用于处理SecureCrt会话文件，已解决重复手动修改每个会话配置
处理逻辑：
1.带参数运行：参数用于设置全局会话保持目录（可从软件全局选项里找到路径，将此路径赋值于变量），生成或更新变量保存文件（默认用户目录.crtconfig）
2.不带参数运行：
a.脚本里硬编程SecureCrt默认全局会话保存目录（按默认配置生成.crtconfig）
b.已存在.crtconfig文件（全局会话目录设置未修改过情况）使用配置文件参数进行设置
依赖：所有会话文件生成都依赖全局默认会话文件
目的：最大化使用用户偏好本地设置，减少脚本硬编程，灵活迁移，无需太多依赖
"""

from __future__ import unicode_literals

import os
import platform
from ConfigParser import ConfigParser

if platform.system() == "Darwin":
    user_home = os.getenv("HOME")
    crt_confdir = os.path.join(user_home, 'Library', 'Application Support', 'VanDyke', 'SecureCRT', 'Config')
    crt_config = os.path.join(user_home, '.crtconfig')

    print 'mac'
elif platform.system() == "Windows":
    user_home = os.getenv("HOMEPATH")
    crt_confdir = os.path.join(user_home, '', '', '')
    crt_config = os.path.join(user_home, '.crtconfig')

if not os.path.exists(crt_config):
    cf = ConfigParser()
    cf.add_section('global')
    cf.set('global', 'loginurl', 'xxx')
    cf.set('global', 'sessionurl', 'abc')
    cf.write(open(crt_config, 'w'))
