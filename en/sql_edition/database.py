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

    # tables
    tables = {"TU":"https://www.tohoku.ac.jp/en/news/university_news/index.html",
              "GLC":"https://www.insc.tohoku.ac.jp/english/",
              "ENGINEER":"https://www.eng.tohoku.ac.jp/english/news/news4/"}

    site_names = {"TU":"University News",
                  "GLC":"Global Learning Center News",
                  "ENGINEER":"Engineering News"}


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
            print("No information")
        else:
            for r in res:
                print(f"id: {r[0]}, date: {r[1]}, title: {r[2]}, new: {r[3]}")

    def now(self, table):
        url = self.tables[table]
        name = self.site_names[table]
        data = self.get(table=table)
        if data is None:
            result = ["="*15, f"No information on {name}.",
                    "Check the official site.", url]
        else:
            tmp = []
            for info in data:
                tmp.append(info)
            header = ["="*15, f"Now, {len(tmp)} information on {name}.", "="*15]
            footer = ["="*15, "Check the official site.", url, ""]
            result = header + tmp + footer
            if table == "TU":
                result.append(f"{'='*15}\nOnline class guide\nhttps://sites.google.com/view/teleclass-tohoku/forstudents\nClick 'English version'\n")
        return "\n".join(self.separate(result))

    def new(self, table, open_flag=True):
        url = self.tables[table]
        name = self.site_names[table]
        data = self.get_new(table=table, open_flag=open_flag)
        if data is not None:
            tmp = []
            for info in data:
                tmp.append(info)
            header = ["="*15, f"New information on {name}.",
                    "Check the official site.", url, "="*15]
            result = header + tmp
            return "\n".join(self.separate(result))
        else:
            return None

    def today(self, table):
        now = datetime.datetime.now(datetime.timezone(
                                            datetime.timedelta(hours=9)))
        date = now.strftime('%Y/%m/%d')

        url = self.tables[table]
        name = self.site_names[table]
        data = self.get_date(table=table, date=date)
        if data is not None:
            tmp = []
            for info in data:
                tmp.append(info)
            header = ["="*15, f"Today, you have {len(tmp)} information on {name}.",
                    "Check the official site.", url, "="*15]
            result = header + tmp
            return "\n".join(self.separate(result))
        else:
            result = ["="*15, f"No update today on {name}.",
                    "Check the official site.", url, "&&&"]
            return "\n".join(self.separate(result))

    def two_week(self, table):
        url = self.tables[table]
        name = self.site_names[table]
        today = datetime.datetime.now(datetime.timezone(
                                            datetime.timedelta(hours=9)))
        two_week_res = []
        for i in range(14):
            date = today - datetime.timedelta(days=i)
            date_str = date.strftime('%Y/%m/%d')
            data = self.get_date(table=table, date=date_str)
            if data is not None:
                two_week_res += data

        if len(two_week_res) > 0:
            header = ["="*15, f"{len(two_week_res)} news on {name} after {date.strftime('%m/%d')}", "="*15]
            footer = [f"Check the official site.", url]
            return "\n".join(self.separate(header + two_week_res + footer))
        else:
            return f"{'='*15}\nNo update on {name} from {date.strftime('%m/%d')}.\nCheck the official site.\n{url}\n{'='*15}"

    def check_new(self):
        for major in self.tables.keys():
            data = self.get_new(table=major, open_flag=False)
            print(major)
            if data is None:
                print("None")
            else:
                print(f"{len(data)} news")

    def register(self, info, override=False):
        '''
        info should have this format
        info = {
            "date": "2020/4/12",
            "target": "TU",
            "content": "\n《4/12》\n*****\nhttps://*****",
        }
        '''
        self.save()
        try:
            db = self.cursor
            date = info["date"]
            table = info["target"]
            content = info["content"]
            contents = ["《" + info for info in content.split("\n《")[1:]]

            if table in self.tables.keys():
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

                for text in contents:
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
        for table in self.tables.keys():
            self.open(table=table)

    def create_table(self, table):
        self.save()
        db = self.cursor
        columns = "(id int unique, time date, content text, new int default 1)"
        term = f"create table if not exists {table} {columns}"
        db.execute(term)
        self.save()

    def start(self):
        for table in self.tables.keys():
            self.create_table(table=table)
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
