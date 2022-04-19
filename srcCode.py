# -*- coding:utf-8 -*-

import time
import urllib.request
import json

import tkinter as tk
import os
from tkinter import filedialog
from ctypes import windll

Header = {
    # 测试过，只加User-Agent的效果是最好的
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
}
prefix = 'https://www1.hkexnews.hk/search/titleSearchServlet.do?'
pdf_url_prefix = 'https://www1.hkexnews.hk'
sortDir = 'sortDir=0&'
sortByOptions = 'sortByOptions=DateTime&'
category = 'category=0&'
market = 'market=SEHK&'
stockId = 'stockId=-1&'  # 实际上stockId与股票代码并不是一一对应的。-1代表用户未指定股票代码
documentType = 'documentType=-1&'
fromDate = 'fromDate=20220228&'
toDate = 'toDate=20220330&'
title = 'title=&'
searchType = 'searchType=1&'
t1code = 't1code=40000&'  # 三个tcode可以定位到年报这个选项
t2Gcode = 't2Gcode=-2&'
t2code = 't2code=40100&'
rowRange = 'rowRange=2000&' # rowRange决定了xhr展示的大小，所以调大一点
lang = 'lang=zh&'  # 这个页面只有繁中以及英文


def dateforward(year, month):
    month = month + 1
    if month > 12:
        month = 1
        year = year + 1
    return year, month


def getPage(FD, TD):
    uurl = prefix + sortDir + sortByOptions + category + market + stockId + \
           documentType + title + searchType + t1code + t2code + t2Gcode + rowRange + lang
    FROM = 'fromDate=' + FD + '&'
    TO = 'toDate=' + TD + '&'
    uurl = uurl + FROM + TO
    print('getting...' + uurl)
    req = urllib.request.Request(url=uurl, headers=Header)
    response = urllib.request.urlopen(req)
    js = json.loads(response.read().decode('utf-8'))
    return json.loads(js['result'])


def Download_pdf(url, final_path_prefix, file_name):
    print('downloading...' + file_name)
    urllib.request.urlretrieve(url, final_path_prefix + '\\' + file_name + '.pdf')


def PageProcess(PageData):
    for i in PageData:
        pdf_url = pdf_url_prefix + str(i['FILE_LINK'])
        stock_code = str(i['STOCK_CODE'])
        stock_name = str(i['STOCK_NAME'])
        stock_title = str(i['TITLE'])
        file_info = str(i['FILE_INFO'])
        if (file_info == '多檔案'):
            continue
        stock_code=stock_code.replace('/',' ').replace('\n','').replace('\r','').replace('|',' ').replace('<',' ').replace('>',' ')
        stock_title = stock_title.replace('/', ' ').replace('\n', '').replace('\r', '').replace('|',' ').replace('<',' ').replace('>',' ')
        file_name = (stock_code + '_' + stock_name + '_' + stock_title) \
            .replace('/', ' ').replace('\n', '').replace('\r', '').replace('|',' ').replace('<',' ').replace('>',' ')
        final_path_prefix = file_path + stock_code + '_' + stock_name
        if not (os.path.isdir(final_path_prefix)):
            try:
                os.makedirs(final_path_prefix)
            except OSError:
                print(
                    "This file has such a strange name that this program could not solve it. check <log.txt> for details")
                with open(file_path+'log.txt', 'a+') as f:
                    f.write('OSError' + ':' + stock_code + '_' + stock_name + '\n')

                continue
        if (os.path.isfile(final_path_prefix + '\\' + file_name + '.pdf')):
            print('This file already exists, we will skip it___' + file_name)
            time.sleep(0.1)  # get rid of anti-reptile system
            continue
        try:
            Download_pdf(pdf_url, final_path_prefix, file_name)
        except urllib.error.HTTPError:
            print("404 Not Found. Invalid pdf_url. it's site's fault")
            with open(file_path+'log.txt', 'a+')as f:
                f.write('HTTPError' + ':' + stock_code + '_' + stock_name + '\n')


if __name__ == '__main__':
    print("Running")
    pre_year, pre_month = 2007, 6
    next_year, next_month = 2007, 7
    # ----------------------让用户选择目标文件夹
    windll.shcore.SetProcessDpiAwareness(2)  # 高清对话框
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askdirectory().replace('/', '\\')
    if (len(file_path) == 0):
        exit(0)
    else:
        file_path = file_path + '\\'
    # --------------------------------------
    while (pre_year < 2022) or (pre_year == 2022 and next_month <= 4):
        if (pre_month < 10):
            pre = str(pre_year) + '0' + str(pre_month) + "01"
        else:
            pre = str(pre_year) + str(pre_month) + "01"
        if (next_month < 10):
            next = str(next_year) + '0' + str(next_month) + "01"
        else:
            next = str(next_year) + str(next_month) + "01"
        pre_year, pre_month = next_year, next_month
        next_year, next_month = dateforward(next_year, next_month)
        PageData = getPage(pre, next)
        PageProcess(PageData)
