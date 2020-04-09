#-*- coding: utf-8 -*-
import os
import pickle
from collections import defaultdict

'''
このInfoクラスを使って、
from info import Info

info = Info()
info.at_first("工学部")
とかすれば最新の情報がstrで返ってくるよ。
'''

class Info:
    major_index = {"全体":"tu.pickle",
                "文学部":"sal.pickle", "文学研究科":"sal.pickle",
                "教育学部":"sed.pickle", "教育学研究科":"sed.pickle",
                "法学部":"law.pickle", "法学研究科":"law.pickle",
                "経済学部":"econ.pickle", "経済学研究科":"econ.pickle",
                "理学部":"sci.pickle", "理学研究科":"sci.pickle",
                "医学部":"med.pickle", "医学系研究科":"med.pickle",
                "歯学部":"dent.pickle", "歯学研究科":"dent.pickle",
                "薬学部":"pharm.pickle", "薬学研究科":"pharm.pickle",
                "工学部":"eng.pickle", "工学研究科":"eng.pickle",
                "農学部":"agri.pickle", "農学研究科":"agri.pickle",
                "国際文化研究科":"intcul.pickle",
                "情報科学研究科":"is.pickle",
                "生命科学研究科":"lifesci.pickle",
                "環境科学研究科":"kankyo.pickle",
                "医工学研究科":"bme.pickle"}
    db_root = os.path.join("..", "sites_db")

    def now(self, major):
        data = self.read(path=self.major_index[major])
        if data is None:
            return f"=====\n{major}に登録された情報はありません。"
        else:
            contents = ["="*5, f"{major}に現在登録されている情報は{len(data)}件です。"]
            for k, v in data.items():
                contents.append(f"{k}\n{v}")
            return "\n".join(contents)

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

    def at_first(self, major):
        contents = ["現時点で登録されている情報です。", self.now("全体"),
                    "東北大学オンライン授業ガイド\nhttps://sites.google.com/view/teleclass-tohoku/forstudents",
                    self.now(major)]
        return "\n".join(contents)
