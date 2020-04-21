#-*- coding: utf-8 -*-
import os
import time
import json
import requests
import datetime
import schedule
from bs4 import BeautifulSoup
from collections import defaultdict

from database import DataBase


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
    url = ""
    majors = []
    override = False

    def get(self):
        #soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり

        return defaultdict(list)

    def request(self):
        print(f"【{self.majors[0]}】Connecting...")
        response = requests.get(self.url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "lxml")
        print("Done!")
        return soup

    def dic(self, info_list=[]):
        tmp = datetime.datetime.strptime("2020/2/1", "%Y/%m/%d")
        limit_date = datetime.date(tmp.year, tmp.month, tmp.day)
        info_list = sorted(info_list, key=lambda x:x.time, reverse=True)
        data = defaultdict(list)
        for item in info_list:
            if item.time >= limit_date:
                data[item.time].append(item.content)
        return data

    def update(self):
        self.data = self.get()
        return self.today, self.override

    @property
    def today(self):
        now = datetime.datetime.now(datetime.timezone(
                                            datetime.timedelta(hours=9)))
        key = datetime.date(now.year, now.month, now.day)
        date = now.strftime('%Y/%m/%d')
        return self.data[key], date

    @property
    def all(self):
        info_list = []
        for key in self.data.keys():
            info_list.append([self.data[key], key.strftime('%Y/%m/%d')])
        return info_list, self.override


class Superviser:
    # posting timers
    _posting = ["10:00", "15:00", "20:00"]

    def __init__(self, targets=[], timers=[], posting=None):
        self.db = DataBase()
        self.slack_webhook_url = os.environ["SLACK_WEBHOOK_URL"]
        self.heroku_domain = os.environ["HEROKU_DOMAIN"]
        self._targets = targets
        self._timers = timers
        if posting:
            self._posting = posting
        for timer in timers:
            schedule.every().day.at(timer).do(self.update)
        for timer in self._posting:
            schedule.every().day.at(timer).do(self.call)
        schedule.every(20).minutes.do(self.knock)

    def update(self):
        for obj in self._targets:
            try:
                response, override = obj.update()
                result = response[0]
                date = response[1]
                if len(result) > 0:
                    print("Changed!")
                    content = "\n" + "\n".join(result)
                    info = {
                        "date":date,
                        "targets":obj.majors,
                        "content":content
                    }
                    res = self.db.register(info=info, override=override)
                    if res:
                        print("Completely updated")
                    else:
                        print("Failed update")
                else:
                    print("No change")
            except:
                error_text = "英語版 {}が対象のサイトがうまくスクレイピングできんかった。。{}".format(obj.majors, obj.url)
                requests.post(self.slack_webhook_url, data=json.dumps({'text':error_text}))

    def call(self):
        print("Checking new information.")
        major_index = self.db.major_index
        for major in major_index.keys():
            try:
                result = self.db.new(major=major)
            except:
                result = None
            if result is not None:
                self.push(message=result, majors=[major])
                print(f"Message pushed >> {major}")
            else:
                print("No new information")

    def run(self):
        while True:
            now = datetime.datetime.now(datetime.timezone(
                                                datetime.timedelta(hours=9)))
            print(now.strftime('%Y/%m/%d %H:%M:%S'))
            schedule.run_pending()
            time.sleep(60)

    def reload(self):
        for obj in self._targets:
            try:
                obj.update()
                data, override = obj.all
                print("Reloading database")
                for dayinfo in data:
                    date = dayinfo[1]
                    if len(dayinfo[0]) > 0:
                        content = "\n" + "\n".join(dayinfo[0])
                        info = {
                            "date":date,
                            "targets":obj.majors,
                            "content":content
                        }
                        res = self.db.register(info=info, override=override)
                        if res:
                            print("Done!")
                        else:
                            print("Failed reload")
            except:
                print("rFailed reload")

    @property
    def targets(self):
        return "\n".join([obj.url for obj in self._targets])

    @property
    def timers(self):
        return "\n".join(self._timers)

    ### line bot apiとの連携用
    def push(self, message, majors, subject="false"):
        data = {"message":message, "majors":majors, "subject":subject}
        res = requests.post(f"{self.heroku_domain}/push", json=json.dumps(data))
        if res.status_code == 200:
            text = f"【英語版 更新報告】\n対象：{majors}\n内容：{message}"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':text}))
        elif res.status_code == 503:
            text = f"【英語版 更新報告】\n対象：{majors}\n内容：{message}\n*status: 配信完了まで時間かかったぽいやつ*"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':text}))
        else:
            error = f"{majors}送信できなかった。。:jobs:＜:ぴえん:"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':error}))

    def knock(self):
        print("定期接続確認...")
        res = requests.get(f"{self.heroku_domain}/remind")
        if res.status_code == 200:
            print("英語版 LINE botサーバー生存確認完了")
        else:
            error = "英語版 LINE botサーバーに問題が生じたぞ！さぁ直すんだ"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':error}))
