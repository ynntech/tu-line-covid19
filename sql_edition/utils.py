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
        print(f"【{self.majors[0]}】接続中...")
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
                    print("更新がありました。")
                    content = "\n" + "\n".join(result)
                    info = {
                        "date":date,
                        "targets":obj.majors,
                        "content":content
                    }
                    res = self.db.register(info=info, override=override)
                    if res:
                        print("登録完了")
                    else:
                        print("正常に登録できませんでした。")
                else:
                    print("更新はありませんでした。")
            except:
                error_text = "{}が対象のサイトがうまくスクレイピングできんかった。。{}".format(obj.majors, obj.url)
                requests.post(self.slack_webhook_url, data=json.dumps({'text':error_text}))

    def call(self):
        print("新着情報がないが確認します。")
        route = self.router.routing()
        if len(route) > 0:
            for major, v in route.keys():
                message = "\n&&&\n".join(v)
                self.push(message=message, major=major)
            print(f"配信完了 >> {major}")
        else:
            print("登録された情報はありません。")

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
                print("情報をデータベースに書き込みます。")
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
                            print("登録完了")
                        else:
                            print("正常に登録できませんでした。")
            except:
                print("reloadできひんかった")

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
            text = f"【更新報告】\n対象：{major}\n内容：{message}"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':text}))
        elif res.status_code == 503:
            text = f"【更新報告】\n対象：{major}\n内容：{message}\n*status: 配信完了まで時間かかったぽいやつ*"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':text}))
        else:
            error = f"{major}送信できなかった。。:jobs:＜:ぴえん:"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':error}))

    def knock(self):
        print("定期接続確認...")
        res = requests.get(f"{self.heroku_domain}/remind")
        if res.status_code == 200:
            print("LINE botサーバー生存確認完了")
        else:
            error = "LINE botサーバーに問題が生じたぞ！さぁ直すんだ"
            requests.post(self.slack_webhook_url, data=json.dumps({'text':error}))

class Router:
    # default setting
    majors = {"文学部":["人文社会学科"],
              "教育学部":["教育科学科"],
              "法学部":["法学科"],
              "経済学部":["経済学科", "経営学科", "未定"],
              "理学部":["数学系","物理系","化学系", "地球科学系","生物系"],
              "医学部":["医学科", "保健学科"],
              "歯学部":["歯学科"],
              "薬学部":["薬学科", "創薬科学科", "未定"],
              "工学部":["機械知能・航空工学科", "電気情報物理工学科", "化学・バイオ工学科",
                       "材料科学総合学科", "建築・社会環境工学科"],
              "農学部":["生物生産科学科", "応用生物化学科", "未定"],
              "文学研究科":[],
              "教育学研究科":[],
              "法学研究科":[],
              "経済学研究科":[],
              "理学研究科":[],
              "医学系研究科":[],
              "歯学研究科":[],
              "薬学研究科":[],
              "工学研究科":[],
              "農学研究科":[],
              "国際文化研究科":[],
              "情報科学研究科":[],
              "生命科学研究科":[],
              "環境科学研究科":[],
              "医工学研究科":[],
              "法科大学院":[],
              "公共政策大学院":[],
              "会計大学院":[]}
    subjects = {}

    def __init__(self):
        self.db = DataBase()

    def get(self):
        # Reset data dictionary
        data = {}
        major_index = self.db.major_index
        for major in major_index.keys():
            try:
                result = self.db.new(major=major)
            except:
                result = None
            data[major] = result
        return data

    def routing(self):
        news = self.get()
        route = {}

        major_tmp = []
        for major in self.majors.keys():
            if news[major] is not None:
                major_tmp.append(major)

        index = defaultdict(list)
        for subject in self.subjects.keys():
            if news[subject] is not None:
                index[self.subjects[subject]].append(subject)

        ## 全学の情報があるとき
        if news["全学生向け"] is not None:
            ## もし学部の情報の更新がなければ、、、
            if len(major_tmp) == 0:
                ## もし学科の更新もなければ、、、
                if len(index) == 0:
                    ## 全学教育の情報があれば
                    if news["全学教育"] is not None:
                        route["全学生向け_not全学教育"] = [news["全学生向け"]]
                        route["全学教育"] = [news["全学生向け"], news["全学教育"]]
                    ## 全学教育の情報がなければ
                    else:
                        route["全学生向け"] = [news["全学生向け"]]
                ## もし学科の更新が1つの学部におさまるとき
                elif len(index) == 1:
                    major = list(index.keys())[0]
                    ## 全学教育の情報があれば
                    if news["全学教育"] is not None:
                        ## 1学科のみ
                        if len(index[major]) == 1:
                            subject = index[major][0]
                            route[f"{major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                news["全学教育"],
                                                                news[subject]]
                            route[f"{major}_{subject}_not全学教育"] = [news["全学生向け"],
                                                                    news[subject]]
                            route[f"{major}_not{subject}_全学教育"] = [news["全学生向け"],
                                                                    news["全学教育"]]
                            route[f"{major}_not{subject}_not全学教育"] = [news["全学生向け"]]
                        ## 2学科更新
                        elif len(index[major]) >= 2:
                            for subject in self.majors[major]:
                                route[f"{major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                    news["全学教育"]]
                                route[f"{major}_{subject}_not全学教育"] = [news["全学生向け"]]
                                if subject in index[major]:
                                    route[f"{major}_{subject}_全学教育"].append(news[subject])
                                    route[f"{major}_{subject}_not全学教育"].append(news[subject])
                        ## 万が一更新なかったとき
                        else:
                            route[f"{major}_全学教育"] = [news["全学生向け"],
                                                        news["全学教育"]]
                            route[f"{major}_not全学教育"] = [news["全学生向け"]]
                        ## 最後にこれ以外の学部
                        route[f"not{major}_全学教育"] = [news["全学生向け"],
                                                        news["全学教育"]]
                        route[f"not{major}_not全学教育"] = [news["全学生向け"]]
                    ## 全学教育の情報がないとき、、、
                    else:
                        ## 1学科のみ
                        if len(index[major]) == 1:
                            subject = index[major][0]
                            route[f"{major}_{subject}"] = [news["全学生向け"],
                                                            news[subject]]
                            route[f"{major}_not{subject}"] = [news["全学生向け"]]
                        ## 2学科更新
                        elif len(index[major]) >= 2:
                            for subject in self.majors[major]:
                                route[f"{major}_{subject}"] = [news["全学生向け"]]
                                if subject in index[major]:
                                    route[f"{major}_{subject}"].append(news[subject])
                        ## 万が一更新なかったとき
                        else:
                            route[major] = [news["全学生向け"]]
                        ## 最後にこれ以外の学部
                        route[f"not{major}"] = [news["全学生向け"]]
                ## もし学科の更新が2つ以上の学部にわたるとき
                else:
                    if news["全学教育"] is not None:
                        for major in self.majors.keys():
                            ## 学科の更新あり
                            if major in index:
                                ## 1学科のみ
                                if len(index[major]) == 1:
                                    subject = index[major][0]
                                    route[f"{major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                        news["全学教育"],
                                                                        news[subject]]
                                    route[f"{major}_{subject}_not全学教育"] = [news["全学生向け"],
                                                                            news[subject]]
                                    route[f"{major}_not{subject}_全学教育"] = [news["全学生向け"],
                                                                            news["全学教育"]]
                                    route[f"{major}_not{subject}_not全学教育"] = [news["全学生向け"]]
                                ## 2学科更新
                                elif len(index[major]) >= 2:
                                    for subject in self.majors[major]:
                                        route[f"{major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                            news["全学教育"]]
                                        route[f"{major}_{subject}_not全学教育"] = [news["全学生向け"]]
                                        if subject in index[major]:
                                            route[f"{major}_{subject}_全学教育"].append(news[subject])
                                            route[f"{major}_{subject}_not全学教育"].append(news[subject])
                                ## 万が一更新なかったとき
                                else:
                                    route[f"{major}_全学教育"] = [news["全学生向け"],
                                                                news["全学教育"]]
                                    route[f"{major}_not全学教育"] = [news["全学生向け"]]
                            ## 学科の更新なし
                            else:
                                ## lenが0だと大学院
                                if len(self.majors[major]) == 0:
                                    route[major] = [news["全学生向け"]]
                                else:
                                    route[f"{major}_全学教育"] = [news["全学生向け"],
                                                                news["全学教育"]]
                                    route[f"{major}_not全学教育"] = [news["全学生向け"]]
                    ## 全学教育なし
                    else:
                        for major in self.majors.keys():
                            if major in index:
                                if len(index[major]) == 1:
                                    subject = index[major][0]
                                    route[f"{major}_{subject}"] = [news["全学生向け"],
                                                                    news[subject]]
                                    route[f"{major}_not{subject}"] = [news["全学生向け"]]
                                elif len(index[major]) >= 2:
                                    for subject in self.majors[major]:
                                        route[f"{major}_{subject}"] = [news["全学生向け"]]
                                        if subject in index[major]:
                                            route[f"{major}_{subject}"].append(news[subject])
                                else:
                                    route[major] = [news["全学生向け"]]
                            else:
                                route[major] = [news["全学生向け"]]
            ## 学部の情報が1つ更新されたとき
            elif len(major_tmp) == 1:
                main_major = major_tmp[0]
                ## 学科単位の更新はなし
                if len(index) == 0:
                    if news["全学教育"] is not None:
                        if len(self.majors[main_major]) == 0:
                            route[main_major] = [news["全学生向け"],
                                                news[main_major]]
                            route[f"not{main_major}"] = [news["全学生向け"]]
                        else:
                            route[f"{main_major}_全学教育"] = [news["全学生向け"],
                                                            news["全学教育"],
                                                            news[main_major]]
                            route[f"{main_major}_not全学教育"] = [news["全学生向け"],
                                                                news[main_major]]
                            route[f"not{main_major}_全学教育"] = [news["全学生向け"],
                                                                news["全学教育"]]
                            route[f"not{main_major}_not全学教育"] = [news["全学生向け"]]
                    else:
                        route[main_major] = [news["全学生向け"], news[main_major]]
                        route[f"not{main_major}"] = [news["全学生向け"]]
                elif len(index) == 1:
                    sub_major = list(index.keys())[0]
                    if news["全学教育"] is not None:
                        ## 一致するなら学部
                        if main_major == sub_major:
                            if len(index[sub_major]) == 1:
                                subject = index[sub_major][0]
                                route[f"{sub_major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                        news["全学教育"],
                                                                        news[main_major],
                                                                        news[subject]]
                                route[f"{sub_major}_{subject}_not全学教育"] = [news["全学生向け"],
                                                                            news[main_major],
                                                                            news[subject]]
                                route[f"{sub_major}_not{subject}_全学教育"] = [news["全学生向け"],
                                                                            news["全学教育"],
                                                                            news[main_major]]
                                route[f"{sub_major}_not{subject}_not全学教育"] = [news["全学生向け"],
                                                                                news[main_major]]
                            elif len(index[sub_major]) >= 2:
                                for subject in self.majors[sub_major]:
                                    route[f"{sub_major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                                news["全学教育"],
                                                                                news[main_major]]
                                    route[f"{sub_major}_{subject}_not全学教育"] = [news["全学生向け"],
                                                                                news[main_major]]
                                    if subject in index[sub_major]:
                                        route[f"{sub_major}_{subject}_全学教育"].append(news[subject])
                                        route[f"{sub_major}_{subject}_not全学教育"].append(news[subject])
                            else:
                                route[f"{sub_major}_全学教育"] = [news["全学生向け"],
                                                                news["全学教育"],
                                                                news[main_major]]
                                route[f"{sub_major}_not全学教育"] = [news["全学生向け"],
                                                                    news[main_major]]
                            route[f"not{sub_major}_全学教育"] = [news["全学生向け"],
                                                                news["全学教育"]]
                            route[f"not{sub_major}_not全学教育"] = [news["全学生向け"]]
                        else:
                            for major in self.majors.keys():
                                if major == sub_major:
                                    if len(index[sub_major]) == 1:
                                        subject = index[sub_major][0]
                                        route[f"{major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                                news["全学教育"],
                                                                                news[subject]]
                                        route[f"{major}_{subject}_not全学教育"] = [news["全学生向け"],
                                                                                    news[subject]]
                                        route[f"{major}_not{subject}_全学教育"] = [news["全学生向け"],
                                                                                    news["全学教育"]]
                                        route[f"{major}_not{subject}_not全学教育"] = [news["全学生向け"]]
                                    elif len(index[sub_major]) >= 2:
                                        for subject in self.majors[sub_major]:
                                            route[f"{major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                                    news["全学教育"]]
                                            route[f"{major}_{subject}_not全学教育"] = [news["全学生向け"]]
                                            if subject in index[sub_major]:
                                                route[f"{major}_{subject}_全学教育"].append(news[subject])
                                                route[f"{major}_{subject}_not全学教育"].append(news[subject])
                                    else:
                                        route[f"{major}_全学教育"] = [news["全学生向け"],
                                                                    news["全学教育"]]
                                        route[f"{major}_not全学教育"] = [news["全学生向け"]]
                                else:
                                    if len(self.majors[major]) == 0:
                                        route[major] = [news["全学生向け"]]
                                        if major == main_major:
                                            route[major].append(news[main_major])
                                    else:
                                        route[f"{major}_全学教育"] = [news["全学生向け"],
                                                                    news["全学教育"]]
                                        route[f"{major}_not全学教育"] = [news["全学生向け"]]
                                        if major == main_major:
                                            route[f"{major}_全学教育"].append(news[main_major])
                                            route[f"{major}_not全学教育"].append(news[main_major])
                    else:
                        if main_major == sub_major:
                            if len(index[sub_major]) == 1:
                                subject = index[sub_major][0]
                                route[f"{sub_major}_{subject}"] = [news["全学生向け"],
                                                                    news[main_major],
                                                                    news[subject]]
                                route[f"{sub_major}_not{subject}"] = [news["全学生向け"],
                                                                    news[main_major]]
                            elif len(index[sub_major]) >= 2:
                                for subject in self.majors[sub_major]:
                                    route[f"{sub_major}_{subject}"] = [news["全学生向け"],
                                                                        news[main_major]]
                                    if subject in index[sub_major]:
                                        route[f"{sub_major}_{subject}"].append(news[subject])
                            else:
                                route[sub_major] = [news["全学生向け"],
                                                    news[main_major]]
                            route[f"not{sub_major}"] = [news["全学生向け"]]
                        else:
                            for major in self.majors.keys():
                                if major == sub_major:
                                    if len(index[sub_major]) == 1:
                                        subject = index[sub_major][0]
                                        route[f"{major}_{subject}"] = [news["全学生向け"],
                                                                        news[subject]]
                                        route[f"{major}_not{subject}"] = [news["全学生向け"]]
                                    elif len(index[sub_major]) >= 2:
                                        for subject in self.majors[sub_major]:
                                            route[f"{major}_{subject}"] = [news["全学生向け"]]
                                            if subject in index[sub_major]:
                                                route[f"{major}_{subject}"].append(news[subject])
                                    else:
                                        route[major] = [news["全学生向け"]]
                                else:
                                    route[major] = [news["全学生向け"]]
                                    if major == main_major:
                                        route[major].append(news[main_major])
                else:
                    if news["全学教育"] is not None:
                        for major in self.majors.keys():
                            if major in index:
                                if major == main_major:
                                    if len(index[major]) == 1:
                                        subject = index[major][0]
                                        route[f"{major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                            news["全学教育"],
                                                                            news[main_major],
                                                                            news[subject]]
                                        route[f"{major}_{subject}_not全学教育"] = [news["全学生向け"],
                                                                                news[main_major],
                                                                                news[subject]]
                                        route[f"{major}_not{subject}_全学教育"] = [news["全学生向け"],
                                                                                news["全学教育"],
                                                                                news[main_major]]
                                        route[f"{major}_not{subject}_not全学教育"] = [news["全学生向け"],
                                                                                    news[main_major]]
                                    elif len(index[major]) >= 2:
                                        for subject in self.majors[major]:
                                            route[f"{major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                                news["全学教育"],
                                                                                news[main_major]]
                                            route[f"{major}_{subject}_not全学教育"] = [news["全学生向け"],
                                                                                    news[main_major]]
                                            if subject in index[major]:
                                                route[f"{major}_{subject}_全学教育"].append(news[subject])
                                                route[f"{major}_{subject}_not全学教育"].append(news[subject])
                                    else:
                                        route[f"{major}_全学教育"] = [news["全学生向け"],
                                                                    news["全学教育"],
                                                                    news[main_major]]
                                        route[f"{major}_not全学教育"] = [news["全学生向け"],
                                                                        news[main_major]]
                                else:
                                    if len(index[major]) == 1:
                                        subject = index[major][0]
                                        route[f"{major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                            news["全学教育"],
                                                                            news[subject]]
                                        route[f"{major}_{subject}_not全学教育"] = [news["全学生向け"],
                                                                                news[subject]]
                                        route[f"{major}_not{subject}_全学教育"] = [news["全学生向け"],
                                                                                news["全学教育"]]
                                        route[f"{major}_not{subject}_not全学教育"] = [news["全学生向け"]]
                                    elif len(index[major]) >= 2:
                                        for subject in self.majors[major]:
                                            route[f"{major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                                news["全学教育"]]
                                            route[f"{major}_{subject}_not全学教育"] = [news["全学生向け"]]
                                            if subject in index[major]:
                                                route[f"{major}_{subject}_全学教育"].append(news[subject])
                                                route[f"{major}_{subject}_not全学教育"].append(news[subject])
                                    else:
                                        route[f"{major}_全学教育"] = [news["全学生向け"],
                                                                    news["全学教育"]]
                                        route[f"{major}_not全学教育"] = [news["全学生向け"]]
                            else:
                                if len(self.mejors[major]) == 0:
                                    route[major] = [news["全学生向け"]]
                                    if major == main_major:
                                        route[major].append(news[main_major])
                                else:
                                    route[f"{major}_全学教育"] = [news["全学生向け"],
                                                                news["全学教育"]]
                                    route[f"{major}_not全学教育"] = [news["全学生向け"]]
                                    if major == main_major:
                                        route[f"{major}_全学教育"].append(news[main_major])
                                        route[f"{major}_not全学教育"].append(news[main_major])
                    else:
                        for major in self.majors.keys():
                            if major in index:
                                if major == main_major:
                                    if len(index[major]) == 1:
                                        subject = index[major][0]
                                        route[f"{major}_{subject}"] = [news["全学生向け"],
                                                                        news[main_major],
                                                                        news[subject]]
                                        route[f"{major}_not{subject}"] = [news["全学生向け"],
                                                                        news[main_major]]
                                    elif len(index[major]) >= 2:
                                        for subject in self.majors[major]:
                                            route[f"{major}_{subject}"] = [news["全学生向け"],
                                                                            news[main_major]]
                                            if subject in index[major]:
                                                route[f"{major}_{subject}"].append(news[subject])
                                    else:
                                        route[major] = [news["全学生向け"],
                                                        news[main_major]]
                                else:
                                    if len(index[major]) == 1:
                                        subject = index[major][0]
                                        route[f"{major}_{subject}"] = [news["全学生向け"],
                                                                        news[subject]]
                                        route[f"{major}_not{subject}"] = [news["全学生向け"]]
                                    elif len(index[major]) >= 2:
                                        for subject in self.majors[major]:
                                            route[f"{major}_{subject}"] = [news["全学生向け"]]
                                            if subject in index[major]:
                                                route[f"{major}_{subject}"].append(news[subject])
                                    else:
                                        route[major] = [news["全学生向け"]]
                            else:
                                route[major] = [news["全学生向け"]]
                                if major == main_major:
                                    route[major].append(news[main_major])
            elif len(major_tmp) >= 2:
                if news["全学教育"] is not None:
                    for major in self.majors.keys():
                        if major in index:
                            if major in major_tmp:
                                if len(index[major]) == 1:
                                    subject = index[major][0]
                                    route[f"{major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                        news["全学教育"],
                                                                        news[major],
                                                                        news[subject]]
                                    route[f"{major}_{subject}_not全学教育"] = [news["全学生向け"],
                                                                            news[major],
                                                                            news[subject]]
                                    route[f"{major}_not{subject}_全学教育"] = [news["全学生向け"],
                                                                            news["全学教育"],
                                                                            news[major]]
                                    route[f"{major}_not{subject}_not全学教育"] = [news["全学生向け"],
                                                                                news[major]]
                                elif len(index[major]) >= 2:
                                    for subject in self.majors[major]:
                                        route[f"{major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                            news["全学教育"],
                                                                            news[major]]
                                        route[f"{major}_{subject}_not全学教育"] = [news["全学生向け"],
                                                                                news[major]]
                                        if subject in index[major]:
                                            route[f"{major}_{subject}_全学教育"].append(news[subject])
                                            route[f"{major}_{subject}_not全学教育"].append(news[subject])
                                else:
                                    route[f"{major}_全学教育"] = [news["全学生向け"],
                                                                news["全学教育"],
                                                                news[major]]
                                    route[f"{major}_not全学教育"] = [news["全学生向け"],
                                                                    news[major]]
                            else:
                                if len(index[major]) == 1:
                                    subject = index[major][0]
                                    route[f"{major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                        news["全学教育"],
                                                                        news[subject]]
                                    route[f"{major}_{subject}_not全学教育"] = [news["全学生向け"],
                                                                            news[subject]]
                                    route[f"{major}_not{subject}_全学教育"] = [news["全学生向け"],
                                                                            news["全学教育"]]
                                    route[f"{major}_not{subject}_not全学教育"] = [news["全学生向け"]]
                                elif len(index[major]) >= 2:
                                    for subject in self.majors[major]:
                                        route[f"{major}_{subject}_全学教育"] = [news["全学生向け"],
                                                                            news["全学教育"]]
                                        route[f"{major}_{subject}_not全学教育"] = [news["全学生向け"]]
                                        if subject in index[major]:
                                            route[f"{major}_{subject}_全学教育"].append(news[subject])
                                            route[f"{major}_{subject}_not全学教育"].append(news[subject])
                                else:
                                    route[f"{major}_全学教育"] = [news["全学生向け"],
                                                                news["全学教育"]]
                                    route[f"{major}_not全学教育"] = [news["全学生向け"]]
                        else:
                            if len(self.mejors[major]) == 0:
                                route[major] = [news["全学生向け"]]
                                if major in major_tmp:
                                    route[major].append(news[major])
                            else:
                                route[f"{major}_全学教育"] = [news["全学生向け"],
                                                            news["全学教育"]]
                                route[f"{major}_not全学教育"] = [news["全学生向け"]]
                                if major in major_tmp:
                                    route[f"{major}_全学教育"].append(news[major])
                                    route[f"{major}_not全学教育"].append(news[major])
                else:
                    for major in self.majors.keys():
                        if major in index:
                            if major in major_tmp:
                                if len(index[major]) == 1:
                                    subject = index[major][0]
                                    route[f"{major}_{subject}"] = [news["全学生向け"],
                                                                    news[major],
                                                                    news[subject]]
                                    route[f"{major}_not{subject}"] = [news["全学生向け"],
                                                                    news[major]]
                                elif len(index[major]) >= 2:
                                    for subject in self.majors[major]:
                                        route[f"{major}_{subject}"] = [news["全学生向け"],
                                                                        news[major]]
                                        if subject in index[major]:
                                            route[f"{major}_{subject}"].append(news[subject])
                                else:
                                    route[major] = [news["全学生向け"], news[major]]
                            else:
                                if len(index[major]) == 1:
                                    subject = index[major][0]
                                    route[f"{major}_{subject}"] = [news["全学生向け"],
                                                                    news[subject]]
                                    route[f"{major}_not{subject}"] = [news["全学生向け"]]
                                elif len(index[major]) >= 2:
                                    for subject in self.majors[major]:
                                        route[f"{major}_{subject}"] = [news["全学生向け"]]
                                        if subject in index[major]:
                                            route[f"{major}_{subject}"].append(news[subject])
                                else:
                                    route[major] = [news["全学生向け"]]
                        else:
                            route[major] = [news["全学生向け"]]
                            if major in major_tmp:
                                route[major].append(news[major])
        else:
            if len(major_tmp) == 0:
                if len(index) == 0:
                    if news["全学教育"] is not None:
                        route["全学教育"] = [news["全学教育"]]
                elif len(index) == 1:
                    major = list(index.keys())[0]
                    if news["全学教育"] is not None:
                        if len(index[major]) == 1:
                            subject = index[major][0]
                            route[f"{major}_{subject}_全学教育"] = [news["全学教育"],
                                                                    news[subject]]
                            route[f"{major}_{subject}_not全学教育"] = [news[subject]]
                            route[f"{major}_not{subject}_全学教育"] = [news["全学教育"]]
                        elif len(index[major]) >= 2:
                            for subject in self.majors[major]:
                                route[f"{major}_{subject}_全学教育"] = [news["全学教育"]]
                                if subject in index[major]:
                                    route[f"{major}_{subject}_全学教育"].append(news[subject])
                                    route[f"{major}_{subject}_not全学教育"] = [news[subject]]
                        else:
                            route[f"{major}_全学教育"] = [news["全学教育"]]
                        route[f"not{major}_全学教育"] = [news["全学教育"]]
                    else:
                        for subject in index[major]:
                            route[f"{major}_{subject}"] = [news[subject]]
                else:
                    if news["全学教育"] is not None:
                        for major in self.majors.keys():
                            if major in index:
                                if len(index[major]) == 1:
                                    subject = index[major][0]
                                    route[f"{major}_{subject}_全学教育"] = [news["全学教育"],
                                                                        news[subject]]
                                    route[f"{major}_{subject}_not全学教育"] = [news[subject]]
                                    route[f"{major}_not{subject}_全学教育"] = [news["全学教育"]]
                                elif len(index[major]) >= 2:
                                    for subject in self.majors[major]:
                                        route[f"{major}_{subject}_全学教育"] = [news["全学教育"]]
                                        if subject in index[major]:
                                            route[f"{major}_{subject}_全学教育"].append(news[subject])
                                            route[f"{major}_{subject}_not全学教育"] = news[subject]
                                else:
                                    route[f"{major}_全学教育"] = [news["全学教育"]]
                            else:
                                if len(self.majors[major]) > 0:
                                    route[f"{major}_全学教育"] = [news["全学教育"]]
                    else:
                        for major in index.keys():
                            for subject in index[major]:
                                route[f"{major}_{subject}"] = [news[subject]]
            elif len(major_tmp) == 1:
                main_major = major_tmp[0]
                if len(index) == 0:
                    if news["全学教育"] is not None:
                        route[f"{main_major}_全学教育"] = [news["全学教育"],
                                                        news[main_major]]
                        route[f"{main_major}_not全学教育"] = [news[main_major]]
                        route[f"not{main_major}_全学教育"] = [news["全学教育"]]
                    else:
                        route[f"{main_major}"] = [news[main_major]]
                elif len(index) == 1:
                    sub_major = list(index.keys())[0]
                    if news["全学教育"] is not None:
                        if main_major == sub_major:
                            if len(index[sub_major]) == 1:
                                subject = index[sub_major][0]
                                route[f"{sub_major}_{subject}_全学教育"] = [news["全学教育"],
                                                                        news[main_major],
                                                                        news[subject]]
                                route[f"{sub_major}_{subject}_not全学教育"] = [news[main_major],
                                                                            news[subject]]
                                route[f"{sub_major}_not{subject}_全学教育"] = [news["全学教育"],
                                                                            news[main_major]]
                                route[f"{sub_major}_not{subject}_not全学教育"] = [news[main_major]]
                            elif len(index[sub_major]) >= 2:
                                for subject in self.majors[sub_major]:
                                    route[f"{sub_major}_{subject}_全学教育"] = [news["全学教育"],
                                                                                news[main_major]]
                                    route[f"{sub_major}_{subject}_not全学教育"] = [news[main_major]]
                                    if subject in index[sub_major]:
                                        route[f"{sub_major}_{subject}_全学教育"].append(news[subject])
                                        route[f"{sub_major}_{subject}_not全学教育"].append(news[subject])
                            else:
                                route[f"{sub_major}_全学教育"] = [news["全学教育"],
                                                                news[main_major]]
                                route[f"{sub_major}_not全学教育"] = [news[main_major]]
                            route[f"not{sub_major}_全学教育"] = [news["全学教育"]]
                        else:
                            for major in self.majors.keys():
                                if major == sub_major:
                                    if len(index[sub_major]) == 1:
                                        subject = index[sub_major][0]
                                        route[f"{major}_{subject}_全学教育"] = [news["全学教育"],
                                                                                news[subject]]
                                        route[f"{major}_{subject}_not全学教育"] = [news[subject]]
                                        route[f"{major}_not{subject}_全学教育"] = [news["全学教育"]]
                                    elif len(index[sub_major]) >= 2:
                                        for subject in self.majors[sub_major]:
                                            route[f"{major}_{subject}_全学教育"] = [news["全学教育"]]
                                            if subject in index[sub_major]:
                                                route[f"{major}_{subject}_全学教育"].append(news[subject])
                                                route[f"{major}_{subject}_not全学教育"] = [news[subject]]
                                    else:
                                        route[f"{major}_全学教育"] = [news["全学教育"]]
                                else:
                                    if len(self.majors[major]) == 0:
                                        if major == main_major:
                                            route[major] = [news[main_major]]
                                    else:
                                        route[f"{major}_全学教育"] = [news["全学教育"]]
                                        if major == main_major:
                                            route[f"{major}_全学教育"].append(news[main_major])
                                            route[f"{major}_not全学教育"] = [news[main_major]]
                    else:
                        if main_major == sub_major:
                            if len(index[sub_major]) == 1:
                                subject = index[sub_major][0]
                                route[f"{sub_major}_{subject}"] = [news[main_major],
                                                                    news[subject]]
                                route[f"{sub_major}_not{subject}"] = [news[main_major]]
                            elif len(index[sub_major]) >= 2:
                                for subject in self.majors[sub_major]:
                                    route[f"{sub_major}_{subject}"] = [news[main_major]]
                                    if subject in index[sub_major]:
                                        route[f"{sub_major}_{subject}"].append(news[subject])
                            else:
                                route[sub_major] = [news[main_major]]
                        else:
                            route[main_major] = news[main_major]
                            for subject in index[sub_major]:
                                route[f"{sub_major}_{subject}"] = [news[subject]]
                else:
                    if news["全学教育"] is not None:
                        for major in self.majors.keys():
                            if major in index:
                                if major == main_major:
                                    if len(index[major]) == 1:
                                        subject = index[major][0]
                                        route[f"{major}_{subject}_全学教育"] = [news["全学教育"],
                                                                            news[main_major],
                                                                            news[subject]]
                                        route[f"{major}_{subject}_not全学教育"] = [news[main_major],
                                                                                news[subject]]
                                        route[f"{major}_not{subject}_全学教育"] = [news["全学教育"],
                                                                                news[main_major]]
                                        route[f"{major}_not{subject}_not全学教育"] = [news[main_major]]
                                    elif len(index[major]) >= 2:
                                        for subject in self.majors[major]:
                                            route[f"{major}_{subject}_全学教育"] = [news["全学教育"],
                                                                                news[main_major]]
                                            route[f"{major}_{subject}_not全学教育"] = [news[main_major]]
                                            if subject in index[major]:
                                                route[f"{major}_{subject}_全学教育"].append(news[subject])
                                                route[f"{major}_{subject}_not全学教育"].append(news[subject])
                                    else:
                                        route[f"{major}_全学教育"] = [news["全学教育"],
                                                                    news[main_major]]
                                        route[f"{major}_not全学教育"] = [news[main_major]]
                                else:
                                    if len(index[major]) == 1:
                                        subject = index[major][0]
                                        route[f"{major}_{subject}_全学教育"] = [news["全学教育"],
                                                                                news[subject]]
                                        route[f"{major}_{subject}_not全学教育"] = [news[subject]]
                                        route[f"{major}_not{subject}_全学教育"] = [news["全学教育"]]
                                    elif len(index[major]) >= 2:
                                        for subject in self.majors[major]:
                                            route[f"{major}_{subject}_全学教育"] = [news["全学教育"]]
                                            if subject in index[major]:
                                                route[f"{major}_{subject}_全学教育"].append(news[subject])
                                                route[f"{major}_{subject}_not全学教育"] = [news[subject]]
                                    else:
                                        route[f"{major}_全学教育"] = [news["全学教育"]]
                            else:
                                if len(self.majors[major]) == 0:
                                    if major == main_major:
                                        route[major] = [news[main_major]]
                                else:
                                    route[f"{major}_全学教育"] = [news["全学教育"]]
                                    if major == main_major:
                                        route[f"{major}_全学教育"].append(news[main_major])
                                        route[f"{major}_not全学教育"] = [news[main_major]]
                    else:
                        for major in self.majors.keys():
                            if major in index:
                                if major == main_major:
                                    if len(index[major]) == 1:
                                        subject = index[major][0]
                                        route[f"{major}_{subject}"] = [news[main_major],
                                                                        news[subject]]
                                        route[f"{major}_not{subject}"] = [news[main_major]]
                                    elif len(index[major]) >= 2:
                                        for subject in self.majors[major]:
                                            route[f"{major}_{subject}"] = [news[main_major]]
                                            if subject in index[major]:
                                                route[f"{major}_{subject}"].append(news[subject])
                                    else:
                                        route[f"{major}"] = [news[main_major]]
                                else:
                                    for subject in index[major]:
                                        route[f"{major}_{subject}"] = [news[subject]]
                            else:
                                if major == main_major:
                                    route[major] = [news[main_major]]
            elif len(major_tmp) >= 2:
                if news["全学教育"] is not None:
                    for major in self.majors.keys():
                        if major in index:
                            if major in major_tmp:
                                if len(index[major]) == 1:
                                    subject = index[major][0]
                                    route[f"{major}_{subject}_全学教育"] = [news["全学教育"],
                                                                        news[major],
                                                                        news[subject]]
                                    route[f"{major}_{subject}_not全学教育"] = [news[major],
                                                                            news[subject]]
                                    route[f"{major}_not{subject}_全学教育"] = [news["全学教育"],
                                                                            news[major]]
                                    route[f"{major}_not{subject}_not全学教育"] = [news[major]]
                                elif len(index[major]) >= 2:
                                    for subject in self.majors[major]:
                                        route[f"{major}_{subject}_全学教育"] = [news["全学教育"],
                                                                            news[major]]
                                        route[f"{major}_{subject}_not全学教育"] = [news[major]]
                                        if subject in index[major]:
                                            route[f"{major}_{subject}_全学教育"].append(news[subject])
                                            route[f"{major}_{subject}_not全学教育"].append(news[subject])
                                else:
                                    route[f"{major}_全学教育"] = [news["全学教育"],
                                                                news[major]]
                                    route[f"{major}_not全学教育"] = [news[major]]
                            else:
                                if len(index[major]) == 1:
                                    subject = index[major][0]
                                    route[f"{major}_{subject}_全学教育"] = [news["全学教育"],
                                                                        news[subject]]
                                    route[f"{major}_{subject}_not全学教育"] = [news[subject]]
                                    route[f"{major}_not{subject}_全学教育"] = [news["全学教育"]]
                                elif len(index[major]) >= 2:
                                    for subject in self.majors[major]:
                                        route[f"{major}_{subject}_全学教育"] = [news["全学教育"]]
                                        if subject in index[major]:
                                            route[f"{major}_{subject}_全学教育"].append(news[subject])
                                            route[f"{major}_{subject}_not全学教育"] = [news[subject]]
                                else:
                                    route[f"{major}_全学教育"] = [news["全学教育"]]
                        else:
                            if len(self.majors[major]) == 0:
                                if major in major_tmp:
                                    route[major] = [news[major]]
                            else:
                                route[f"{major}_全学教育"] = [news["全学教育"]]
                                if major in major_tmp:
                                    route[f"{major}_全学教育"].append(news[major])
                                    route[f"{major}_not全学教育"] = [news[major]]
                else:
                    for major in self.majors.keys():
                        if major in index:
                            if major in major_tmp:
                                if len(index[major]) == 1:
                                    subject = index[major][0]
                                    route[f"{major}_{subject}"] = [news[major],
                                                                    news[subject]]
                                    route[f"{major}_not{subject}"] = [news[major]]
                                elif len(index[major]) >= 2:
                                    for subject in self.majors[major]:
                                        route[f"{major}_{subject}"] = [news[major]]
                                        if subject in index[major]:
                                            route[f"{major}_{subject}"].append(news[subject])
                                else:
                                    route[major] = [news[major]]
                            else:
                                if len(index[major]) >= 1:
                                    for subject in self.majors[major]:
                                        if subject in index[major]:
                                            route[f"{major}_{subject}"] = [news[subject]]
                        else:
                            if major in major_tmp:
                                route[major] = [news[major]]
        return route
