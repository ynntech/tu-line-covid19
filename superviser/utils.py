#-*- coding: utf-8 -*-
import os
import time
import json
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
    majors = []

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
        print(f"【{self.majors[0]}】接続中...")
        response = requests.get(self.url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "lxml")
        print("Done!")
        return soup

    def dic(self, info_list=[]):
        tmp = datetime.datetime.strptime("2020年2月1日", "%Y年%m月%d日")
        limit_date = datetime.date(tmp.year, tmp.month, tmp.day)
        info_list = sorted(info_list, key=lambda x:x.time, reverse=True)
        data = defaultdict(list)
        for item in info_list:
            if item.time >= limit_date:
                data[item.time].append(item.content)
        return data

    def update(self):
        pre = self.data.copy()
        post = self.get()
        diff = self.diff(pre, post)
        self.data = post
        self.write()
        return diff

    def diff(self, pre, post):
        print("前回との変更を抽出中...")
        change = post.copy()
        for key in pre.keys():
            if (post[key] == pre[key]) and (pre[key] != []):
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
                #ata = defaultdict(list)
                #data_row = pickle.load(f)
                #for d in data_row:
                #    data[d[0]] = d[1]
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


class Superviser:
    def __init__(self, targets=[], timers=[]):
        self.slack_webhook_url = os.environ["SLACK_WEBHOOK_URL"]
        self.heroku_domain = os.environ["HEROKU_DOMAIN"]
        self._targets = targets
        self._timers = timers
        for timer in timers:
            schedule.every().day.at(timer).do(self.call)
        schedule.every(20).minutes.do(self.knock)

    def call(self, post=True):
        print("定期実行中")
        for obj in self._targets:
            try:
                result = obj.new
                if result is not None:
                    contents = ["新規情報があります。",
                                "公式サイトもご確認ください。", obj.url,
                                "="*15]
                    for v in result.values():
                        if len(v) > 0:
                            for info in v:
                                contents.append(info)
                    message = "\n".join(contents)
                    ## line api, push message
                    print(obj.majors, contents)
                    self.push(message=message, majors=obj.majors)
                else:
                    print("更新はありません")
            except:
                error_text = "{}のサイトで正常にデータ更新できなかったぞ！\n{}".format(obj.majors[0], obj.url)
                requests.post(self.slack_webhook_url, data=json.dumps({'text':error_text}))

    def run(self):
        while True:
            now = datetime.datetime.now(datetime.timezone(
                                                datetime.timedelta(hours=9)))
            print(now.strftime('%Y/%m/%d %H:%M:%S'))
            schedule.run_pending()
            time.sleep(60)

    @property
    def targets(self):
        return "\n".join([obj.url for obj in self._targets])

    @property
    def timers(self):
        return "\n".join(self._timers)

    ### line bot apiとの連携用
    def push(self, message, majors, subject="false"):
        data = {"message":message, "majors":majors, "subject":subject}
        requests.post(f"{self.heroku_domain}/push", json=json.dump(data))
        if res.status_code == 200:
            text = f"【更新報告】\n対象：{majors}\n内容：{message}"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':text}))
        else:
            error = f"{majors}送信できなかった。。:jobs:＜:ぴえん:"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':error}))

    def knock(self):
        print("定期接続確認...")
        res = requests.get(f"{self.heroku_domain}/remind")
        if res.status_code == 200:
            print("LINE botサーバー生存確認完了")
        else:
            error = "LINE botサーバーに問題が生じたぞ！さぁ直すんだ"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':error}))
