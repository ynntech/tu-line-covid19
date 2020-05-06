#-*- coding: utf-8 -*-
import os
import MySQLdb
import json
import datetime
import random

class DataBase:
    HOST = os.environ["MYSQL_HOST"]
    USER = os.environ["MYSQL_USER"]
    PASSWD = os.environ["MYSQL_PSSWD"]
    DB = os.environ["MYSQL_DB"]
    # major indexes
    major_index = {"全学生向け":"http://www.bureau.tohoku.ac.jp/covid19BCP/index.html",
                   "全学教育":"http://www2.he.tohoku.ac.jp/zengaku/zengaku.html",
                   "文学部":"https://www.sal.tohoku.ac.jp/jp/news/covid19.html",
                   "文学研究科":"https://www.sal.tohoku.ac.jp/jp/news/covid19.html",
                   "教育学部":"https://www.sed.tohoku.ac.jp/news.html",
                   "教育学研究科":"https://www.sed.tohoku.ac.jp/news.html",
                   "法学部":"http://www.law.tohoku.ac.jp/covid19/",
                   "法学研究科":"http://www.law.tohoku.ac.jp/covid19/",
                   "経済学部":"https://sites.google.com/view/rinji-econ-tohoku-ac-jp/",
                   "経済学研究科":"https://sites.google.com/view/rinji-econ-tohoku-ac-jp/",
                   "理学部":"https://www.sci.tohoku.ac.jp/news/20200305-10978.html",
                   "理学研究科":"https://www.sci.tohoku.ac.jp/news/20200305-10978.html",
                   "医学部":"https://www.med.tohoku.ac.jp/admissions/2003announce/index.html",
                   "医学系研究科":"https://www.med.tohoku.ac.jp/admissions/2003announce/index.html",
                   "歯学部":"http://www.dent.tohoku.ac.jp/important/202003.html",
                   "歯学研究科":"http://www.dent.tohoku.ac.jp/important/202003.html",
                   "薬学部":"http://www.pharm.tohoku.ac.jp/info/200331/200331.shtml",
                   "薬学研究科":"http://www.pharm.tohoku.ac.jp/info/200331/200331.shtml",
                   "工学部":"https://www.eng.tohoku.ac.jp/news/detail-,-id,1561.html",
                   "工学研究科":"https://www.eng.tohoku.ac.jp/news/detail-,-id,1561.html",
                   "農学部":"https://www.agri.tohoku.ac.jp/jp/news/covid-19/",
                   "農学研究科":"https://www.agri.tohoku.ac.jp/jp/news/covid-19/",
                   "国際文化研究科":"http://www.intcul.tohoku.ac.jp/",
                   "情報科学研究科":"https://www.is.tohoku.ac.jp/jp/forstudents/detail---id-2986.html",
                   "生命科学研究科":"https://www.lifesci.tohoku.ac.jp/outline/covid19_taiou/",
                   "環境科学研究科":"http://www.kankyo.tohoku.ac.jp/index.html",
                   "医工学研究科":"http://www.bme.tohoku.ac.jp/information/news/",
                   "法科大学院":"http://www.law.tohoku.ac.jp/covid19/",
                   "公共政策大学院":"http://www.law.tohoku.ac.jp/covid19/",
                   "会計大学院":"https://sites.google.com/view/rinji-econ-tohoku-ac-jp/"}

    def __init__(self):
        self.connect()

    def connect(self):
        self.connection = MySQLdb.connect(host=self.HOST, db=self.DB,
                                        user=self.USER, passwd=self.PASSWD,
                                        charset="utf8")
        self.cursor = self.connection.cursor()

    def save(self):
        self.connection.commit()

    def exit(self):
        self.connection.close()

    def get(self, table):
        self.save()
        # timeの日付の順番で取得
        term = f"select content from {table} order by time desc"
        self.cursor.execute(term)
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        else:
            return [r[0] for r in res]

    def get_date(self, table, date):
        self.save()
        # timeの一致するものを取得
        term = f"select content from {table} where time=\'{date}\'"
        self.cursor.execute(term)
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        else:
            return [r[0] for r in res]

    def get_new(self, table, open_flag=True):
        self.save()
        # newの値が1のものを抽出
        term = f"select content from {table} where new=1 order by time desc"
        self.cursor.execute(term)
        res = self.cursor.fetchall()
        # 取得後全てのnewフラグを0にして既出情報扱いに
        if open_flag:
            term = f"update {table} set new=0"
            self.cursor.execute(term)
            self.save()
        if len(res) == 0:
            return None
        else:
            return [r[0] for r in res]

    def get_all(self, table):
        self.save()
        term = f"select * from {table} order by time desc"
        self.cursor.execute(term)
        res = self.cursor.fetchall()
        if len(res) == 0:
            print("何も登録されていません。")
        else:
            for r in res:
                print(f"id: {r[0]}, date: {r[1]}, title: {r[2]}, new: {r[3]}")

    def now(self, major):
        url = self.major_index[major]
        data = self.get(table=major)
        if data is None:
            return f"{'='*15}\n{major}に登録された情報はありません。\n公式サイトをご確認ください\n{url}\n{'='*15}"
        else:
            contents = []
            for info in data:
                contents.append(info)
            header = ["="*15, f"{major}に現在登録されている情報は{len(contents)}件です。", "="*15]
            if major == "全学生向け":
                contents.append(f"{'='*15}\n東北大学オンライン授業ガイド\nhttps://sites.google.com/view/teleclass-tohoku/forstudents")
            contents.append(f"公式サイトもご確認ください\n{url}")
            return "\n".join(self.separate(header + contents))

    def new(self, major, open_flag=True):
        url = self.major_index[major]
        data = self.get_new(table=major, open_flag=open_flag)
        if data is not None:
            contents = [f"{major}の新規情報があります。",
                        "公式サイトもご確認ください。", url,
                        "="*15]
            for info in data:
                contents.append(info)
            return "\n".join(self.separate(contents))
        else:
            return None

    def today(self, major):
        url = self.major_index[major]
        now = datetime.datetime.now(datetime.timezone(
                                            datetime.timedelta(hours=9)))
        date = now.strftime('%Y/%m/%d')
        data = self.get_date(table=major, date=date)
        if data is not None:
            data.append(f"公式サイトもご確認ください\n{url}")
            header = ["="*15, f"{major}に本日登録された情報は{len(data)-1}件です。", "="*15]
            return "\n".join(self.separate(header + data))
        else:
            return f"{'='*15}\n{major}に本日登録された情報はありません。\n公式サイトをご確認ください\n{url}\n{'='*15}"

    def two_week(self, major):
        url = self.major_index[major]
        today = datetime.datetime.now(datetime.timezone(
                                            datetime.timedelta(hours=9)))
        two_week_res = []
        for i in range(14):
            date = today - datetime.timedelta(days=i)
            date_str = date.strftime('%Y/%m/%d')
            data = self.get_date(table=major, date=date_str)
            if data is not None:
                two_week_res += data

        if len(two_week_res) > 0:
            header = ["="*15, f"{date.strftime('%m/%d')}以降{major}に登録された情報は{len(two_week_res)}件です。", "="*15]
            footer = [f"公式サイトもご確認ください\n{url}"]
            return "\n".join(self.separate(header + two_week_res + footer))
        else:
            return f"{'='*15}\n{date.strftime('%m/%d')}以降{major}に登録された情報はありません。\n公式サイトをご確認ください\n{url}\n{'='*15}"

    def check_new(self):
        for major in self.major_index.keys():
            data = self.get_new(table=major, open_flag=False)
            print(major)
            if data is None:
                print("None")
            else:
                print(f"{len(data)}件")

    def register(self, info, override=False):
        '''
        info should have this format
        info = {
            "date": "2020/4/12",
            "targets": ["***"],
            "content": "\n《4/12》\n*****\nhttps://*****",
        }
        '''
        self.save()
        try:
            db = self.cursor
            date = info["date"]
            targets = info["targets"]
            content = info["content"]
            contents = ["《" + info for info in content.split("\n《")[1:]]

            for table in targets:
                if table in self.major_index.keys():
                    target = f"into {table}"
                    db.execute(f"select max(id) from {table}")
                    _id = db.fetchone()[0]
                    if not _id:
                        _id = 0
                    else:
                        _id = int(_id)
                    # 既にある情報は除外するため、同日にある情報の取得
                    exists_today = self.get_date(table=table, date=date)
                    if exists_today is None:
                        exists_today = []
                    # 既にある情報の取得
                    exists_all = self.get(table=table)
                    if exists_all is None:
                        exists_all = []
                    else:
                        exists_all = [info.split("》")[-1] for info in exists_all]

                    for i in range(len(contents)):
                        text = contents[i]
                        if override and (text.split("》")[-1] in exists_all):
                            term = f"delete from {table} where content=\'{text}\'"
                            db.execute(term)
                            _id += 1
                            v = f"({_id}, \'{date}\', \'{text}\')"
                            term = f"insert {target} (id, time, content) values {v}"
                            db.execute(term)
                            self.save()
                        elif text not in exists_today:
                            _id += 1
                            v = f"({_id}, \'{date}\', \'{text}\')"
                            term = f"insert {target} (id, time, content) values {v}"
                            db.execute(term)
                            self.save()
            return True
        except:
            return False

    def open(self, table):
        self.save()
        self.get_new(table=table)

    def open_all(self):
        for major in self.major_index.keys():
            self.open(table=major)

    def create_table(self, name):
        self.save()
        db = self.cursor
        columns = "(id int unique, time date, content text, new int default 1)"
        term = f"create table if not exists {name} {columns}"
        db.execute(term)
        self.save()

    def start(self):
        for major in self.major_index.keys():
            self.create_table(name=major)
        self.reset()

    def reset_table(self, table):
        self.save()
        db = self.cursor
        term = f"delete from {table}"
        db.execute(term)
        self.save()

    def reset(self):
        db = self.cursor
        term = "show tables"
        db.execute(term)
        res = db.fetchall()
        for r in res:
            self.reset_table(table=r[0])

    def read(self, table, ids=[]):
        self.save()
        db = self.cursor
        for _id in ids:
            term = f"update {table} set new=0 where id={_id}"
            db.execute(term)
            self.save()

    def flag(self, table, ids=[]):
        self.save()
        db = self.cursor
        for _id in ids:
            term = f"update {table} set new=1 where id={_id}"
            db.execute(term)
            self.save()

    def drop(self, table, ids=[]):
        self.save()
        db = self.cursor
        for _id in ids:
            term = f"delete from {table} where id={_id}"
            db.execute(term)
            self.save()

    def separate(self, obj):
        result = []
        tmp = ""
        for string in obj:
            if len(tmp) + len(string) <= 2000:
                tmp += "\n"
                tmp += string
            else:
                result.append("&&&")
                tmp = string
            result.append(string)
        return result

    def __del__(self):
        self.save()
        self.exit()
