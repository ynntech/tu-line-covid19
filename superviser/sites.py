#-*- coding: utf-8 -*-
import os
import re
import datetime

from utils import News, Site


### 全学生向け ###
class TUNews(News):
    def __init__(self, tag, base_url):
        '''
        <parameter>
        tag (bs4.element.Tag) : single topic object
        '''
        self.tag = tag
        self.base_url = base_url
        self.summary()

    ## this should be overrided
    ## because the format of news will be different from the others
    def summary(self):
        contents = "".join(self.tag.text.split("（")[:-1])
        time = self.tag.text.split("（")[-1].split("）")[0]
        href = self.tag.get("href")
        if href[0:4] != "http":
                href = self.base_url + href
        self.content = f"《{time}》\n{contents}\n{href}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        tmp = datetime.datetime.strptime(timestr, "%Y年%m月%d日")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class TU(Site):
    path = os.path.join("..", os.path.join("sites_db", "tu.pickle"))
    url = "http://www.tohoku.ac.jp/japanese/disaster/outbreak/01/outbreak0101/"
    base_url = "http://www.tohoku.ac.jp"
    major = ["全学生向け"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        boxes = soup.find_all("ul", class_="linkStyleA")
        info_list1 = boxes[0].find_all("a")
        info_list2 = boxes[1].find_all("a")
        h3_tags = soup.find("div", class_="webContent").find_all("h3")
        info_list3 = self.abstract(h3_tags)
        info_list = info_list1 + info_list2 + info_list3
        ### 固定情報
        stick1 = TUNews(info_list1[0], self.base_url)
        stick1_url = "http://www.tohoku.ac.jp/japanese/newimg/newsimg/gakusei_20200302_0330.pdf"
        stick1.time = stick1.timeobj(timestr="2020年3月30日")
        stick1.content = f"《2020年3月30日》\n学生のみなさんへの要請事項\n{stick1_url}"
        ###
        info_list = [TUNews(info, self.base_url) for info in info_list]
        info_list.append(stick1)
        return  self.dic(info_list)

    def abstract(self, h3_tags, start="学生のみなさんへ", stop="留学生のみなさんへ（For new international students）"):
        text_list = [tag.text for tag in h3_tags]
        start_tag = h3_tags[text_list.index(start)]
        stop_text = h3_tags[text_list.index(stop)].find_previous("a").text
        info_list = []

        while True:
            start_tag = start_tag.find_next("a")
            if start_tag.text != stop_text:
                if bool(re.search(r'[0-9]', start_tag.text)):
                    info_list.append(start_tag)
            else:
                break
        return info_list


### 文学部・文学研究科 ###
class SalNews(News):
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
        self.time = ""
        self.content = ""

    def timeobj(self, timestr=""):
        year = "2020."
        tmp = datetime.datetime.strptime(year + timestr, "%Y.%m.%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class Sal(Site):
    path = os.path.join("..", os.path.join("sites_db", "sal.pickle"))
    url = "https://www.sal.tohoku.ac.jp/jp/news/covid19.html"
    base_url = "https://www.sal.tohoku.ac.jp/"
    major = ["文学部", "文学研究科"]

    def get(self):
        soup = self.request()
        info_list_comp = []
        info_list = soup.find("article").find_all("section")[:-1]
        grade_list = [str(info.find("h3"))[4:-5] for info in info_list] # 各行の対象学年を格納
        info_list_ = [info.find("tr") for info in info_list] # サイトの各行はtrタグ
        for num, info in enumerate(info_list_):
            if info.find("a") is not None: # aタグが存在している行だけ処理していく
                href = self.base_url + info.find("a").get("href")
                time_tmp = info.find("a").get("href").split("_")[-2][4:] #ファイル名から日付を取得
                time = "{}.{}".format(int(time_tmp[:2]), int(time_tmp[2:])) 
                school = "文学部" if num < 3 else "大学院文学研究科" # 上から何番目のsectionタグかで学部か大学院かを判断
                event = info.find("th").text # 対象の行事を取得
                contents = "{} {}の{}について".format(school, grade_list[num], event) 
                stick = SalNews(info_list[0].find("a"))
                stick.time = stick.timeobj(timestr=time)
                stick.content = "《{}》\n{}\n{}".format(time, contents, href)
                info_list_comp.append(stick)

        #その他の固定情報（日付をサイトの更新日と同じにしている）
        # stick1 = SalNews(info_list[0].find("a"))
        # stick1_url = "https://www.sal.tohoku.ac.jp/jp/news/covid19.html"
        # stick1.time = stick1.timeobj(timestr=time)
        # stick1.content = f"《{time}》\n2020年度 文学部・文学研究科のスケジュールについて\n{stick1_url}"
        # info_list_comp.append(stick1)
        return self.dic(info_list_comp)


### 教育学部・教育学研究科 ###
class SedNews(News):
    def __init__(self, tag, base_url):
        '''
        <parameter>
        tag (bs4.element.Tag) : single topic object
        '''
        self.tag = tag
        self.base_url = base_url
        self.summary()

    ## this should be overrided
    ## because the format of news will be different from the others
    def summary(self):
        contents = self.tag.text.split("｜")[0]
        href = self.tag.get("href")
        if href[0:4] != "http":
            href = self.base_url + "/" + href.split("./")[-1]
        time_split = self.tag.text.split("|")[-1].split(".")[-2:]
        time = "{}.{}".format(str(int(time_split[0])), str(int(time_split[1])))
        self.content = f"《{time}》\n{contents}\n{href}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        year = "2020."
        tmp = datetime.datetime.strptime(year + timestr, "%Y.%m.%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class Sed(Site):
    path = os.path.join("..", os.path.join("sites_db", "sed.pickle"))
    url = "https://www.sed.tohoku.ac.jp/news.html"
    base_url = "https://www.sed.tohoku.ac.jp"
    major = ["教育学部", "教育学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("div", class_="inner").find_all("ul")[0].find_all("a")
        info_list = [SedNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)


### 法学部・法学研究科 ###
class LawNews(News):
    def __init__(self):
        '''
        <parameter>
        tag (bs4.element.Tag) : single topic object
        '''
        self.summary()

    ## this should be overrided
    ## because the format of news will be different from the others
    def summary(self):
        self.time = ""
        self.content = ""

    def timeobj(self, timestr=""):
        year = "2020."
        tmp = datetime.datetime.strptime(year + timestr, "%Y.%m.%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class Law(Site):
    path = os.path.join("..", os.path.join("sites_db", "law.pickle"))
    url = "http://www.law.tohoku.ac.jp/covid19/"
    base_url = "http://www.law.tohoku.ac.jp"
    major = ["法学部", "法学研究科"]

    def get(self):
        soup = self.request()
        info_list = []
        permanent1 = LawNews()
        time = soup.find(class_="law-sub-contents pos-left").find("p").text.split("：")[-1]
        time = "{}.{}".format(time.split("/")[0], time.split("/")[1])
        permanent1.content = "《{}》\n新コロナウイルス感染症（COVID-19）への対応についてが更新されました\n{}".format(time, self.url)
        permanent1.time = permanent1.timeobj(timestr=time)
        info_list.append(permanent1)
        return self.dic(info_list)


### 経済学部・経済学研究科 ###
class EconNews:
    def __init__(self, data):
        self.data = data
        self.summary()

    ## this should be overrided
    ## because the format of news will be different from the others
    def summary(self):
        split_text = self.data.split("\\n")
        content = split_text[0].split("タイトル：")[-1]
        time = split_text[1].split("発信日：")[-1]
        self.content = f"《{time}》\n{content}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        tmp = datetime.datetime.strptime(timestr, "%Y年%m月%d日")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class Econ(Site):
    path = os.path.join("..", os.path.join("sites_db", "econ.pickle"))
    ### ここは特例でGoogle documentやで。頑張ろうな
    url = "https://docs.google.com/document/d/19ArkoemdFSNdgeF0XQO8mI3QNhjkUbXp2lrewNGh1qQ/edit"
    major = ["経済学部", "経済学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        blocks = soup.find_all("script")
        for i in range(len(blocks)):
            if blocks[i].text[0:18] == "DOCS_modelChunk = ":
                block = blocks[i]
                break
        info_list = block.text.split("{")[1].split("}")[0].split('"')[-2].split("----------上から順に新しい情報となります----------\\n")[1:]
        info_list = [EconNews(info) for info in info_list]
        ### 固定情報
        info_list[-1].content += "\n\n詳細はこちら\nhttps://sites.google.com/view/rinji-econ-tohoku-ac-jp/"
        ###
        return self.dic(info_list)


### 理学部・理学研究科 ###
class SciNews(News):
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
        contents = "".join(self.tag.text.split("（")[:-1])
        time = self.tag.text.split("（")[-1].split("）")[0]
        href = self.tag.get("href")
        self.content = f"《{time}》\n{contents}\n{href}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        year = "2020/"
        tmp = datetime.datetime.strptime(year + timestr, "%Y/%m/%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class Sci(Site):
    path = os.path.join("..", os.path.join("sites_db", "sci.pickle"))
    url = "https://www.sci.tohoku.ac.jp/news/20200305-10978.html"
    major = ["理学部", "理学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        li_blocks = soup.find("ul", id="localNav").find_all("li")
        info_list1, ex = self.abstract(li_block=li_blocks[2])
        info_list2, ex = self.abstract(li_block=li_blocks[3], exception=ex)
        info_list3, ex = self.abstract(li_block=li_blocks[4], exception=ex)
        info_list = info_list1 + info_list2 + info_list3
        info_list = [SciNews(info) for info in info_list]
        return self.dic(info_list)

    def abstract(self, li_block=[], exception=[]):
        result = []
        for tag in li_block.find_all("a"):
            if tag.text not in exception:
                href = tag.get("href")
                if href is not None:
                    if href[0:4] != "http":
                        result.append(tag)
                        exception.append(tag.text)
                    elif href.split("/")[2] != "www.tohoku.ac.jp":
                        result.append(tag)
                        exception.append(tag.text)
        return result, exception


### 医学部・医学系研究科 ###
class MedNews(News):
    def __init__(self, tag, base_url):
        '''
        <parameter>
        tag (bs4.element.Tag) : single topic object
        '''
        self.tag = tag
        self.base_url = base_url
        self.summary()

    ## this should be overrided
    ## because the format of news will be different from the others
    def summary(self):
        if self.tag.text[-1] == "）":
            time = self.tag.text.split("（")[-1].split("）")[0]
            contents = self.tag.text[:(-2 - len(time))]
        else:
            time = re.findall(r"\d+/\d+", self.tag.text)[-1]
            contents = self.tag.text[:(-len(time))]
        href = "#" + self.tag.find("a").get("id")
        href = self.base_url + href
        self.content = f"《{time}》\n{contents}\n{href}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        year = "2020/"
        tmp = datetime.datetime.strptime(year + timestr, "%Y/%m/%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class Med(Site):
    path = os.path.join("..", os.path.join("sites_db", "med.pickle"))
    url = "https://www.med.tohoku.ac.jp/admissions/2003announce/index.html"
    major = ["医学部", "医学系研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("div", class_="wrap_contarea sp_contarea area_u-layer_cont").find_all("h4")[:-1]
        info_list = [MedNews(info, self.url) for info in info_list]
        return self.dic(info_list)


### 歯学部・歯学研究科 ###
class DentNews(News):
    def __init__(self, tag, base_url):
        '''
        <parameter>
        tag (bs4.element.Tag) : single topic object
        '''
        self.tag = tag
        self.base_url = base_url
        self.summary()

    ## this should be overrided
    ## because the format of news will be different from the others
    def summary(self):
        contents = "".join(self.tag.text.split("（")[:-1])
        time_split = self.tag.text.split("（")[-1].split("/")
        time = '{}/{}'.format(time_split[0], re.sub("\\D", "", time_split[-1]))
        href = self.tag.get("href")
        if href[0:4] != "http":
            href = self.base_url + "/" + href.split("./")[-1]
        self.content = f"《{time}》\n{contents}\n{href}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        year = "2020/"
        tmp = datetime.datetime.strptime(year + timestr, "%Y/%m/%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class Dent(Site):
    path = os.path.join("..", os.path.join("sites_db", "dent.pickle"))
    url = "http://www.dent.tohoku.ac.jp/important/202003.html"
    base_url = "http://www.dent.tohoku.ac.jp/important"
    major = ["歯学部", "歯学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        ### 学部の新着はindex 1
        info_list = soup.find_all("ul", class_="important_contents")[1].find_all("a")
        ### 固定情報
        stick1 = DentNews(info_list[0], self.base_url)
        stick1_url = "http://www.dent.tohoku.ac.jp/important/202003.html"
        stick1.time = stick1.timeobj(timestr="4/8")
        stick1.content = f"《4/8》\n東北大学行動指針をレベル３へ引き上げ\n{stick1_url}"
        stick2 = DentNews(info_list[0], self.base_url)
        stick2_url = "http://www.dent.tohoku.ac.jp/important/202003.html"
        stick2.time = stick1.timeobj(timestr="4/1")
        stick2.content = f"《4/1》\n緊急！新型コロナウイルス感染症蔓延を防ぐための対応要請\n{stick2_url}"
        ###
        info_list = [DentNews(info, self.base_url) for info in info_list[:-1]]
        info_list.append(stick1)
        info_list.append(stick2)
        return self.dic(info_list)


### 薬学部・薬学研究科 ###
class PharmNews(News):
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
        time = re.search("\d+/\d+", self.tag.text).group()
        contents = self.tag.text.split(time)[-1].split()[-1]
        href = self.tag.get("href")
        self.content = f"《{time}》\n{contents}\n{href}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        year = "2020/"
        tmp = datetime.datetime.strptime(year + timestr, "%Y/%m/%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class Pharm(Site):
    path = os.path.join("..", os.path.join("sites_db", "pharm.pickle"))
    url = "http://www.pharm.tohoku.ac.jp/info/200331/200331.shtml"
    major = ["薬学部", "薬学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("div", class_="contents_wrap_box").find_all("a")
        info_list = self.abstract(info_list)
        ### 固定情報
        stick1 = PharmNews(info_list[0])
        stick1_url = "http://www.pharm.tohoku.ac.jp/info/200331/200331.shtml"
        stick1.time = stick1.timeobj(timestr="4/10")
        stick1.content = f"《4/10》\n学生の入構制限について\n{stick1_url}"
        ###
        info_list = [PharmNews(info) for info in info_list]
        info_list.append(stick1)
        return self.dic(info_list)

    def abstract(self, a_tags):
        info_list = []
        for tag in a_tags:
            if tag.text != "こちら":
                href = tag.get("href")
                if (href[0:4] == "http") and (href.split("/")[2] != "www.tohoku.ac.jp"):
                    info_list.append(tag)
        return info_list


### 工学部・工学研究科 ###
class EngNews(News):
    def __init__(self, tag, base_url):
        '''
        <parameter>
        tag (bs4.element.Tag) : single topic object
        '''
        self.tag = tag
        self.base_url = base_url
        self.summary()

    ## this should be overrided
    ## because the format of news will be different from the others
    def summary(self):
        time_tag = self.tag.find_next("td")
        time_split = time_tag.text.split(".")
        time = "{}.{}".format(time_split[0], re.search(r'\d+', (time_split[1])).group())
        a_tag = self.tag.find("a")
        if a_tag is not None:
            href = a_tag.get("href")
            if href[0:4] != "http":
                href = self.base_url + href
            self.content = f"《{time}》\n{a_tag.text}\n{href}"
        else:
            content = "\n".join(time_tag.find_next("td").text.split())
            url = "https://www.eng.tohoku.ac.jp/news/detail-,-id,1561.html"
            self.content = f"《{time}》\n{content}\n{url}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        year = "2020."
        tmp = datetime.datetime.strptime(year + timestr, "%Y.%m.%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class Eng(Site):
    path = os.path.join("..", os.path.join("sites_db", "eng.pickle"))
    url = "https://www.eng.tohoku.ac.jp/news/detail-,-id,1561.html"
    base_url = "https://www.eng.tohoku.ac.jp"
    major = ["工学部", "工学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="main").find_all("tr")
        info_list = self.abstract(info_list)
        ### 固定情報
        stick1 = EngNews(info_list[0], self.base_url)
        contents = ["《4/10》",
                    "【新型コロナウイルス感染拡大防止のための自宅待機のお願い】",
                    "令和2年4月9日(木)から5月6日(水)まで、原則として登校を禁止し、研究室活動を制限します",
                    "https://www.eng.tohoku.ac.jp/news/detail-,-id,1582.html",
                    "https://www.eng.tohoku.ac.jp/news/detail-,-id,1581.html"]
        stick1.time = stick1.timeobj(timestr="4.10")
        stick1.content = "\n".join(contents)

        stick2 = EngNews(info_list[0], self.base_url)
        contents = ["《4/10》",
                    "【全学生 要回答】東北大ID受取確認(新入生対象), 遠隔授業の受講環境等の調査を実施しています。",
                    "https://www.eng.tohoku.ac.jp/news/detail-,-id,1576.html#survey"]
        stick2.time = stick1.timeobj(timestr="4.10")
        stick2.content = "\n".join(contents)
        sticks = [stick1, stick2]
        ###
        info_list = [EngNews(info, self.base_url) for info in info_list]
        info_list = sticks + info_list
        return self.dic(info_list)

    def abstract(self, tags=[]):
        result = []
        exception = []
        for tag in tags:
            if tag.text not in exception:
                result.append(tag)
                exception.append(tag.text)
        return result


### 農学部・農学研究科 ###
class AgriNews(News):
    def __init__(self, tag, base_url):
        '''
        <parameter>
        tag (bs4.element.Tag) : single topic object
        '''
        self.tag = tag
        self.base_url = base_url
        self.summary()

    ## this should be overrided
    ## because the format of news will be different from the others
    def summary(self):
        time = re.search("\d+.\d+", self.tag.text).group()
        contents = self.tag.text.split("更新　")[-1]
        href = self.tag.get("href")
        if href[0:4] != "http":
            href = self.base_url + href
        self.content = f"《{time}》\n{contents}\n{href}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        year = "2020."
        tmp = datetime.datetime.strptime(year + timestr, "%Y.%m.%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class Agri(Site):
    path = os.path.join("..", os.path.join("sites_db", "agri.pickle"))
    url = "https://www.agri.tohoku.ac.jp/jp/news/covid-19/"
    base_url = "https://www.agri.tohoku.ac.jp/jp/news/covid-19/"
    major = ["農学部", "農学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("div", class_="area_news_cont").find_all("a")
        info_list = [AgriNews(info, self.url) for info in info_list]
        return self.dic(info_list)


### 国際文化研究科 ###
class IntculNews(News):
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
        time = self.tag.find("th").text
        a_tags = self.tag.find_all("a")
        contents = []
        links = []
        for i in range(len(a_tags)):
            href = a_tags[i].get("href")
            links.append(href)
            contents.append(a_tags[i].text)
        contents = "\n".join(contents)
        links = "\n".join(links)
        self.content = f"《{time}》\n{contents}\n{links}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        tmp = datetime.datetime.strptime(timestr, "%Y年%m月%d日")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class Intcul(Site):
    path = os.path.join("..", os.path.join("sites_db", "intcul.pickle"))
    url = "http://www.intcul.tohoku.ac.jp/"
    major = ["国際文化研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find_all("tr")
        info_list = [IntculNews(info) for info in info_list]
        return self.dic(info_list)


### 情報科学研究科 ###
class ISNews(News):
    def __init__(self, tag, base_url):
        '''
        <parameter>
        tag (bs4.element.Tag) : single topic object
        '''
        self.tag = tag
        self.base_url = base_url
        self.summary()

    ## this should be overrided
    ## because the format of news will be different from the others
    def summary(self):
        split_text = self.tag.text.split("（")
        time = re.search("\d+.\d+.\d+", split_text[-1]).group()
        contents = "（".join(split_text[:-1])
        href = self.tag.get("href")
        if href[0:4] != "http":
            href = self.base_url + href
        self.content = f"《{time}》\n{contents}\n{href}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        tmp = datetime.datetime.strptime(timestr, "%Y.%m.%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class IS(Site):
    path = os.path.join("..", os.path.join("sites_db", "is.pickle"))
    url = "https://www.is.tohoku.ac.jp/jp/forstudents/detail---id-2986.html"
    base_url = "https://www.is.tohoku.ac.jp/"
    major = ["情報科学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = []
        boxes = soup.find_all("ul", class_="border")
        for box in boxes:
            info_list.extend(box.find_all("a"))
        info_list = [ISNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)


### 生命科学研究科 ###
class LifesciNews(News):
    month_dic = {"January":"1", "Jan":"1", "February":"2", "Feb":"2", "March":"3", "Mar":"3",
                             "April":"4", "Apr":"4", "May":"5", "June":"6", "July":"7", "August":"8", "Aug":"8",
                            "September":"9", "Sept":"9", "October":"10", "Oct":"10", "November":"11", "Nov":"11",
                            "December":"12", "Dec":"12"}

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
        content = self.tag.find("a").text
        time = self.tag.text.split("(")[-1].split(" update")[0].strip("～").replace('\xa0', ' ')
        href = self.tag.find("a").get("href")
        self.content = f"《{time}》\n{content}\n{href}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        year = "2020/"
        month, day = re.split("[ .]", timestr)[:2]

        date = year +self. month_dic[month] + "/" + day
        tmp = datetime.datetime.strptime(date, "%Y/%m/%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class Lifesci(Site):
    path = os.path.join("..", os.path.join("sites_db", "lifesci.pickle"))
    url = "https://www.lifesci.tohoku.ac.jp/outline/covid19_taiou/"
    major = ["生命科学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("div", id="main").find_all("div")
        info_list = self.abstract(info_list)
        info_list = [LifesciNews(info) for info in info_list]
        return self.dic(info_list)

    def abstract(self, tags):
        result = []
        for tag in tags:
            a = tag.find("a")
            if a is not None:
                text = tag.text
                if "update" in text:
                    result.append(tag)
        return result


### 環境科学研究科 ###
class KankyoNews(News):
    def __init__(self, tag, base_url):
        '''
        <parameter>
        tag (bs4.element.Tag) : single topic object
        '''
        self.tag = tag
        self.base_url = base_url
        self.summary()

    ## this should be overrided
    ## because the format of news will be different from the others
    def summary(self):
        time = self.tag.find("p").text.split(" | ")[-1]
        a_tags = self.tag.find_all("a")
        contents = self.tag.text.split(" | " + time)[-1].split("\r")[0]
        links = []
        for i in range(len(a_tags)):
            href = a_tags[i].get("href")
            if href[0:4] != "http":
                href = self.base_url + href
            links.append(href)
            links = "\n".join(links)
        self.content = f"《{time}》{contents}\n{links}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        tmp = datetime.datetime.strptime(timestr, "%Y/%m/%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class Kankyo(Site):
    path = os.path.join("..", os.path.join("sites_db", "kankyo.pickle"))
    url = "http://www.kankyo.tohoku.ac.jp/index.html"
    base_url = "http://www.kankyo.tohoku.ac.jp/"
    major = ["環境科学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [KankyoNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)


### 医工学研究科 ###
class BmeNews(News):
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
        self.time = self.timeobj(time)
        self.content = " ".join(contents) + "\n" + "\n".join(links)

    def timeobj(self, timestr=""):
        tmp = datetime.datetime.strptime(timestr, "%Y年%m月%d日")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class Bme(Site):
    path = os.path.join("..", os.path.join("sites_db", "bme.pickle"))
    url = "http://www.bme.tohoku.ac.jp/information/news/"
    major = ["医工学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("div", class_="list-news").find_all("li")
        info_list = [BmeNews(info) for info in info_list]
        return self.dic(info_list)
