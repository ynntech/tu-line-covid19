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
    table = ""
    override = False

    def get(self):
        #soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり

        return defaultdict(list)

    def request(self):
        print(f"【{self.table}】Connecting...")
        response = requests.get(self.url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "lxml")
        print("Done!")
        return soup

    def dic(self, info_list=[], limit="2020/2/1"):
        tmp = datetime.datetime.strptime(limit, "%Y/%m/%d")
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
    _posting = ["20:00"]

    def __init__(self, targets=[], timers=[], posting=None):
        self.db = DataBase()
        self.router = Router()
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
                        "target":obj.table,
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
                error_text = "英語版 {}が対象のサイトがうまくスクレイピングできんかった。。{}".format(obj.table, obj.url)
                requests.post(self.slack_webhook_url, data=json.dumps({'text':error_text}))

    def call(self):
        print("Checking new information.")
        route = self.router.routing()
        if len(route) > 0:
            for major, v in route.keys():
                message = "\n&&&\n".join(v)
                self.push(message=message, major=major)
            print(f"Message pushed")
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
                            "target":obj.table,
                            "content":content
                        }
                        res = self.db.register(info=info, override=override)
                        if res:
                            print("Done!")
                        else:
                            print("Failed reload")
            except:
                print("Failed reload")

    @property
    def targets(self):
        return "\n".join([obj.url for obj in self._targets])

    @property
    def timers(self):
        return "\n".join(self._timers)

    ### line bot apiとの連携用
    def push(self, message, major):
        data = {"message":message, "major":major}
        res = requests.post(f"{self.heroku_domain}/push", json=json.dumps(data))
        if res.status_code == 200:
            text = f"【英語版 更新報告】\n内容：{message}"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':text}))
        elif res.status_code == 503:
            text = f"【英語版 更新報告】\n内容：{message}\n*status: 配信完了まで時間かかってるぽいやつ*"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':text}))
        else:
            error = f"英語版、送信できなかった。。:jobs:＜:ぴえん:"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':error}))

    def knock(self):
        print("定期接続確認...")
        res = requests.get(f"{self.heroku_domain}/remind")
        if res.status_code == 200:
            print("英語版 LINE botサーバー生存確認完了")
        else:
            error = "英語版 LINE botサーバーに問題が生じたぞ！さぁ直すんだ"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':error}))


class Router:
    def __init__(self):
        self.db = DataBase()

    def all_week(self):
        # Reset data dictionary
        data = {}
        tables = self.db.tables
        for table in tables.keys():
            try:
                result = self.db.two_week(table=table)
            except:
                result = None
            data[table] = result
        if data["TU"] is not None:
            if data["GLC"] is not None:
                all_news = data["TU"] + "\n&&&\n" + data["GLC"]
            else:
                all_news = data["TU"]
        else:
            if data["GLC"] is not None:
                all_news = data["GLC"]
            else:
                all_news = None
        result = {"TU":all_news}
        for k in data.keys():
            if str(k) not in ["TU", "GLC"]:
                result[k] = data[k]
        return result

    def all_new(self):
        # Reset data dictionary
        data = {}
        tables = self.db.tables
        for table in tables.keys():
            try:
                result = self.db.new(table=table)
            except:
                result = None
            data[table] = result
        if data["TU"] is not None:
            if data["GLC"] is not None:
                all_news = data["TU"] + "\n&&&\n" + data["GLC"]
            else:
                all_news = data["TU"]
        else:
            if data["GLC"] is not None:
                all_news = data["GLC"]
            else:
                all_news = None
        result = {"TU":all_news}
        for k in data.keys():
            if str(k) not in ["TU", "GLC"]:
                result[k] = data[k]
        return result

    def now(self, major):
        news = self.all_week()
        major = major.split("_")
        if len(major) == 1:
            if major[0] == "TU":
                return news["TU"]
            else:
                return None
        elif len(major) == 2:
            if major[0] == "TU":
                result = []
                if news["TU"] is not None:
                    result.append(news["TU"])
                if "not" not in major[1]:
                    table = major[1]
                    if table in news:
                        if news[table] is not None:
                            result.append(news[table])
                if len(result) > 0:
                    return "\n&&&\n".join(result)
                else:
                    return None
            else:
                return None
        else:
            None

    def routing(self):
        news = self.all_new()
        route = {}

        if news["TU"] is not None:
            if news["ENGINEER"] is not None:
                route["TU_ENGINEER"] = [news["TU"], news["ENGINEER"]]
                route["TU_notENGINEER"] = [news["TU"]]
            else:
                route["TU"] = [news["TU"]]
        return route
