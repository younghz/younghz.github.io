#!/usr/bin/python
# -*- coding:utf-8 -*-

__author__ = 'yanghaizhi'

import time
import sys
import os

#get current time
dateString = time.strftime('%Y-%m-%d', time.localtime())
# get title
title = sys.argv[1]
#get file name
fileName = dateString + '-' + title + '.md'
print '文件名称:' + fileName

if (os.path.exists(fileName)):
    print '文件名已经存在，你怎么能写两篇一样的文章？'
    # end
    sys.exit(0)

# create file
print '\n创建文件' + fileName + '成功'
toBeCreateFile = open(fileName, 'w');
toBeWriteToFile = '''--- \nlayout: post \ntitle: "title name" \ntagline: "child title" \ndescription: "" \n\
category: book \ntags: [book] \n--- \n{% include JB/setup %'''

try:
    toBeCreateFile.write(toBeWriteToFile)

finally:
    toBeCreateFile.close()

print '\n结束 ^-^ 尽情写文章吧 ^-^ ...'