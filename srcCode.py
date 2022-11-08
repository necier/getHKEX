# -*- coding:utf-8 -*-
import copy
import time
import urllib.request
import urllib.parse
import urllib.error
import json
import tkinter as tk
import os
from tkinter import filedialog
from ctypes import windll

# 请自行调整爬取的时间区间[年份，月份]
CONFIG = {
    'startDate': [2007, 6],
    'endDate': [2022, 10]
}

Header = {
    # 测试过，只加User-Agent的效果是最好的
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/99.0.4844.51 Safari/537.36',
}
prefix = 'https://www1.hkexnews.hk/search/titleSearchServlet.do?'
pdf_url_prefix = 'https://www1.hkexnews.hk'

Param = {
    'sortDir': '0',
    'sortByOptions': 'DateTime',
    'category': '0',
    'market': 'SEHK',
    'stockId': '-1',
    'documentType': '-1',
    'fromDate': '20220228',  # 初始化时随便设的值，后面getPage()会改成正确的值
    'toDate': '20220330',  # 初始化时随便设的值，后面getPage()会改成正确的值
    'title': '',
    'searchType': '1',
    't1code': '40000',
    't2Gcode': '-2',
    't2code': '40100',
    'rowRange': '2000',
    'lang': 'zh'
}


class Date(object):
    def __init__(self, config):
        self.preDate = None
        self.day = '01'
        self.currentDate = copy.deepcopy(CONFIG['startDate'])
        self.endDate = copy.deepcopy(CONFIG['endDate'])

    def timeAdvance(self):
        self.currentDate[1] += 1
        if self.currentDate[1] > 12:
            self.currentDate[1] = 1
            self.currentDate[0] += 1

    def returnDateInterval(self) -> list:
        res = []
        self.preDate = copy.deepcopy(self.currentDate)
        self.timeAdvance()
        res.append(str(self.preDate[0]) + str.zfill(str(self.preDate[1]), 2) + self.day)
        res.append(str(self.currentDate[0]) + str.zfill(str(self.currentDate[1]), 2) + self.day)
        return res

    def dateCheck(self) -> bool:
        return self.currentDate == self.endDate


# 清除字符串中多余的字符，便于后期处理
def strstd(s):
    return s.replace('/', ' ').replace('\n', '').replace('\r', '').replace('|', ' ').replace('<', ' ').replace('>', ' ')


def getPage(FD, TD):
    Param['fromDate'] = FD
    Param['toDate'] = TD

    data = urllib.parse.urlencode(Param)
    uurl = prefix + data
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
        if file_info == '多檔案':  # 这里必须是繁体，别乱改
            continue
        stock_code = strstd(stock_code)
        stock_title = strstd(stock_title)
        file_name = strstd(stock_code + '_' + stock_name + '_' + stock_title)
        final_path_prefix = file_path + stock_code + '_' + stock_name
        if not (os.path.isdir(final_path_prefix)):
            try:
                os.makedirs(final_path_prefix)
            except OSError:
                print(
                    "This file's name is unsolvable. check <log.txt> for details")
                with open(file_path + 'log.txt', 'a+') as f:
                    f.write('OSError' + ':' + stock_code + '_' + stock_name + '\n')
                continue
        if os.path.isfile(final_path_prefix + '\\' + file_name + '.pdf'):
            print('This file already exists, we will skip it___' + file_name)
            time.sleep(0.1)  # get rid of anti-reptile system
            continue
        try:
            Download_pdf(pdf_url, final_path_prefix, file_name)
        except urllib.error.HTTPError:
            print("404 Not Found. Invalid pdf_url. it's site's fault")
            with open(file_path + 'log.txt', 'a+') as f:
                f.write('HTTPError' + ':' + stock_code + '_' + stock_name + '\n')


if __name__ == '__main__':
    print("Running")
    # -----------------获取文件保存路径
    windll.shcore.SetProcessDpiAwareness(2)  # 高清对话框
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askdirectory().replace('/', '\\')
    if len(file_path) == 0:
        exit(0)
    else:
        file_path = file_path + '\\'
    # -------------------
    date = Date(CONFIG)
    while True:
        dateList = date.returnDateInterval()
        print(dateList)
        PageData = getPage(dateList[0], dateList[1])
        PageProcess(PageData)
        if date.dateCheck():
            break
