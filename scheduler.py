import os
import time
import pickle
import requests
import datetime
import schedule
from bs4 import BeautifulSoup
from collections import defaultdict


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
        print("現在の情報")
        data = defaultdict(list)
        for item in info_list:
            print(f"時刻: {item.time}\n内容: {item.content}")
            data[item.time] = item.content
        return data

    def update(self):
        pre = self.read()
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
                data = pickle.load(f)
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


class BMENews(News):
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
        time = self.tag.find(class_="day").text.split()[0]
        content = self.tag.find_all(class_="detail")
        contents = []
        links = []
        for i in range(len(content)):
            href = content[i].find("a").get("href")
            links.append(href)
            contents.append(content[i].text)
        self.time = time
        self.content = " ".join(contents) + "\n" + "\n".join(links)


class BME(Site):
    path = "./sample_bme.pickle"
    url = "http://www.bme.tohoku.ac.jp/information/news/"

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("div", class_="list-news").find_all("li")
        info_list = [BMENews(info) for info in info_list]
        return self.dic(info_list)


class Superviser:
    def __init__(self, targets=[], timers=[]):
        self._targets = targets
        self._timers = timers
        for timer in timers:
            schedule.every().day.at(timer).do(self.call)

    def call(self):
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        print(f"呼び出し時刻: {now.strftime('%Y/%m/%d %H:%M')}")
        for obj in self._targets:
            print(obj.new)

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(60)

    @property
    def targets(self):
        return "\n".join([obj.url for obj in self._targets])

    @property
    def timers(self):
        return "\n".join(self._timers)
