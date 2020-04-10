#-*- coding: utf-8 -*-
import os
import sys
import time
import pickle
import requests
import datetime
import schedule
from bs4 import BeautifulSoup
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join("..", "linebot")))

from push_message import push_message


class News:
    def __init__(self, tag):
        '''
        <parameter>
        tag (bs4.element.Tag) : single topic object
        '''
        self.tag = tag
        self.summary()

    ## this should be overrided
    ## because the format of news will be different from the others
    def summary(self):
        ## 以降、サイトに合わせて書き直す必要あり
        self.time = None
        self.content = None


class Site:
    path = ""
    url = ""
    major = ""

    def __init__(self):
        self.data = self.read()

    def get(self):
        #soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり

        #info_list = soup.find("div", class_="list-news").find_all("li")
        #info_list = [BMENews(info) for info in info_list]

        #return self.dic(info_list)
        return defaultdict(list)

    def request(self):
        print("接続中...")
        response =  requests.get(self.url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "lxml")
        print("Done!")
        return soup

    def dic(self, info_list=[]):
        info_list = sorted(info_list, key=lambda x:x.time, reverse=True)
        data = defaultdict(list)
        for item in info_list:
            data[item.time].append(item.content)
        return data

    def update(self):
        pre = self.data.copy()
        post = self.get()
        self.data = post
        self.write()
        return self.diff(pre, post)

    def diff(self, pre, post):
        print("前回との変更を抽出中...")
        change = post.copy()
        for key in pre.keys():
            if post[key] == pre[key]:
                del change[key]

        if len(change) > 0:
            print("更新がありました")
            return change
        else:
            print("前回からの変更はありませんでした")
            return None

    def write(self):
        print("データベースの書き換え中...")
        with open(self.path, 'wb') as f:
            pickle.dump(self.data, f)
        print("Done!")

    def read(self):
        print("データベースを読み込み中...")
        if os.path.exists(self.path):
            with open(self.path, 'rb') as f:
                data = defaultdict(list)
                data_row = pickle.load(f)
                for d in data_row:
                    data[d[0]] = d[1]
                print("Done!")
            return data
        else:
            print("ファイルが見つかりませんでした。新規に作成します。")
            return defaultdict(list)

    @property
    def new(self):
        return self.update()

    @property
    def now(self):
        return self.data


class Superviser:
    def __init__(self, targets=[], timers=[]):
        self._targets = targets
        self._timers = timers
        for timer in timers:
            schedule.every().day.at(timer).do(self.call)
        self.call(post=False)

    def call(self, post=True):
        print("定期実行中")
        for obj in self._targets:
            result = obj.new
            if result is not None:
                contents = ["新規情報があります。",
                            "公式サイトもご確認ください。", obj.url,
                            "="*15]
                for v in result.values():
                    for info in v:
                        contents.append(info)
                message = "\n".join(contents)
                ## line api, push message
                for major in obj.major:
                    print(major, contents)
                    if post:
                        push_message(message=message, major=major)

    def run(self):
        while True:
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
            print(now.strftime('%Y/%m/%d %H:%M:%S'))
            schedule.run_pending()
            time.sleep(60)

    @property
    def targets(self):
        return "\n".join([obj.url for obj in self._targets])

    @property
    def timers(self):
        return "\n".join(self._timers)
