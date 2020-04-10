#-*- coding: utf-8 -*-
import os
import pickle
from collections import defaultdict

'''
このInfoクラスを使って、
from info import Info

info = Info()
info.now("工学部")
とかすれば最新の情報がstrで返ってくるよ。
'''

class Info:
    major_index = {"全学生向け":["tu.pickle", "http://www.tohoku.ac.jp/japanese/disaster/outbreak/01/outbreak0101/"],
                "文学部":["sal.pickle", "https://www.sal.tohoku.ac.jp/jp/news/covid19.html"],
                "文学研究科":["sal.pickle", "https://www.sal.tohoku.ac.jp/jp/news/covid19.html"],
                "教育学部":["sed.pickle", "https://www.sed.tohoku.ac.jp/news.html"],
                "教育学研究科":["sed.pickle", "https://www.sed.tohoku.ac.jp/news.html"],
                "法学部":["law.pickle", "http://www.law.tohoku.ac.jp/covid19/"],
                "法学研究科":["law.pickle", "http://www.law.tohoku.ac.jp/covid19/"],
                "経済学部":["econ.pickle", "https://sites.google.com/view/rinji-econ-tohoku-ac-jp/"],
                "経済学研究科":["econ.pickle", "https://sites.google.com/view/rinji-econ-tohoku-ac-jp/"],
                "理学部":["sci.pickle", "https://www.sci.tohoku.ac.jp/news/20200305-10978.html"],
                "理学研究科":["sci.pickle", "https://www.sci.tohoku.ac.jp/news/20200305-10978.html"],
                "医学部":["med.pickle", "https://www.med.tohoku.ac.jp/admissions/2003announce/index.html"],
                "医学系研究科":["med.pickle", "https://www.med.tohoku.ac.jp/admissions/2003announce/index.html"],
                "歯学部":["dent.pickle", "http://www.dent.tohoku.ac.jp/important/202003.html"],
                "歯学研究科":["dent.pickle", "http://www.dent.tohoku.ac.jp/important/202003.html"],
                "薬学部":["pharm.pickle", "http://www.pharm.tohoku.ac.jp/info/200331/200331.shtml"],
                "薬学研究科":["pharm.pickle", "http://www.pharm.tohoku.ac.jp/info/200331/200331.shtml"],
                "工学部":["eng.pickle", "https://www.eng.tohoku.ac.jp/news/detail-,-id,1561.html"],
                "工学研究科":["eng.pickle", "https://www.eng.tohoku.ac.jp/news/detail-,-id,1561.html"],
                "農学部":["agri.pickle", "https://www.agri.tohoku.ac.jp/jp/news/covid-19/"],
                "農学研究科":["agri.pickle", "https://www.agri.tohoku.ac.jp/jp/news/covid-19/"],
                "国際文化研究科":["intcul.pickle", "http://www.intcul.tohoku.ac.jp/"],
                "情報科学研究科":["is.pickle", "https://www.is.tohoku.ac.jp/jp/forstudents/detail---id-2986.html"],
                "生命科学研究科":["lifesci.pickle", "https://www.lifesci.tohoku.ac.jp/outline/covid19_taiou/"],
                "環境科学研究科":["kankyo.pickle", "http://www.kankyo.tohoku.ac.jp/index.html"],
                "医工学研究科":["bme.pickle", "http://www.bme.tohoku.ac.jp/information/news/"]}
    db_root = os.path.join("..", "sites_db")

    def now(self, major):
        path, url = self.major_index[major]
        data = self.read(path=path)
        if data is None:
            return f"{'='*15}\n{major}に登録された情報はありません。\n公式サイトを\
                    ご確認ください\n{url}\n{'='*15}"
        else:
            contents = []
            count = 0
            for v in data.values():
                for info in v:
                    contents.append(info)
                    count += 1
            if major == "全学生向け":
                contents.append(f"{'='*15}\n東北大学オンライン授業ガイド\nhttps://\
                            sites.google.com/view/teleclass-tohoku/forstudents")
            contents.append(f"公式サイトもご確認ください\n{url}")
            header = ["="*15, f"{major}に現在登録されている情報は{count}件です。", "="*15]
            return "\n".join(header + contents)

    def read(self, path):
        path = os.path.join(self.db_root, path)
        print(f"データベースを読み込み中 >> {path}")
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = pickle.load(f)
                print("Done!")
            return data
        else:
            print("ファイルが見つかりませんでした。")
            return None
