# -*- coding: utf-8 -*-
import os
import re
import datetime
from collections import defaultdict

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

    # this should be overrided
    # because the format of news will be different from the others
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
    majors = ["全学生向け"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        boxes = soup.find_all("ul", class_="linkStyleA")
        info_list1 = boxes[0].find_all("a")
        info_list2 = boxes[1].find_all("a")
        h3_tags = soup.find("div", class_="webContent").find_all("h3")
        info_list3 = self.abstract(h3_tags)
        info_list = info_list1 + info_list2 + info_list3
        # 固定情報
        stick1 = TUNews(info_list1[0], self.base_url)
        stick1_url = "http://www.tohoku.ac.jp/japanese/newimg/newsimg/gakusei_20200302_0330.pdf"
        stick1.time = stick1.timeobj(timestr="2020年3月30日")
        stick1.content = f"《2020年3月30日》\n学生のみなさんへの要請事項\n{stick1_url}"
        ###
        info_list = [TUNews(info, self.base_url) for info in info_list]
        info_list.append(stick1)
        return self.dic(info_list)

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


class BCPNews:
    def __init__(self, dt_tag, dd_tag, base_url):
        self.dt_tag = dt_tag
        self.dd_tag = dd_tag
        self.base_url = base_url
        self.summary()

    # this should be overrided
    # because the format of news will be different from the others
    def summary(self):
        contents = self.dd_tag.text
        time = self.dt_tag.text
        href = self.dd_tag.find("a").get("href")
        if href[:4] != "http":
            href = self.base_url + href
        self.content = f"《{time}》\n{contents}\n{href}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        tmp = datetime.datetime.strptime(timestr, "%Y/%m/%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)


class BCP(Site):
    path = os.path.join("..", os.path.join("sites_db", "bcp.pickle"))
    url = "https://www.bureau.tohoku.ac.jp/covid19BCP/latest-info.html"
    base_url = "https://www.bureau.tohoku.ac.jp/covid19BCP/"
    majors = ["全学生向け"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        box = soup.find("section", id="new")
        info_list = self.abstract(box)
        info_list = [BCPNews(info[0], info[1], self.base_url) for info in info_list]
        return self.dic(info_list)

    def abstract(self, box):
        dt_tags = box.find_all("dt")
        return [(dt_tag, dt_tag.find_next("dd")) for dt_tag in dt_tags]


### 全学教育 ###
class GenNews(News):
    def __init__(self, info, base_url1, base_url2):
        '''
        <parameter>
        tag (bs4.element.Tag) : single topic object
        '''
        self.tag = info["tag"]
        self.time = info["time"]
        self.base_url1 = base_url1
        self.base_url2 = base_url2
        self.summary()

    # this should be overrided
    # because the format of news will be different from the others
    def summary(self):
        contents = self.tag.text
        href = self.tag.get("href")
        if href[:4] != "http":
            if href[0] == "/":
                href = self.base_url2 + href
            else:
                href = self.base_url1 + href
        self.content = f"《{self.time}》\n{contents}\n{href}"
        self.time = self.timeobj(self.time)

    def timeobj(self, timestr=""):
        tmp = datetime.datetime.strptime(timestr, "%Y/%m/%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)


class Gen(Site):
    path = os.path.join("..", os.path.join("sites_db", "gen.pickle"))
    url = "http://www2.he.tohoku.ac.jp/zengaku/zengaku.html"
    base_url1 = "http://www2.he.tohoku.ac.jp/zengaku/"
    base_url2 = "http://www2.he.tohoku.ac.jp"
    majors = ["全学教育"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("table").find_all("tr")
        info_list = [GenNews(info, self.base_url1, self.base_url2) for info in self.abstract(info_list)]
        return self.dic(info_list)

    def abstract(self, tags):
        result = []
        for tag in tags:
            if tag.find("td", class_="date"):
                time = tag.find("td", class_="date").text
                if (tag.find("a") and time[:4] == "2020"):
                    result.append({"tag":tag.find("a"), "time":time})
        return result

    def dic(self, info_list=[]):
        tmp = datetime.datetime.strptime("2020年4月1日", "%Y年%m月%d日")
        limit_date = datetime.date(tmp.year, tmp.month, tmp.day)
        info_list = sorted(info_list, key=lambda x:x.time, reverse=True)
        data = defaultdict(list)
        for item in info_list:
            if item.time >= limit_date:
                data[item.time].append(item.content)
        return data


### 文学部・文学研究科 ###
class SalNews:
    # this should be overrided
    # because the format of news will be different from the others
    def summary(self):
        self.time = ""
        self.content = ""

    def timeobj(self, timestr=""):
        year = "2020年"
        tmp = datetime.datetime.strptime(year + timestr, "%Y年%m月%d日")
        return datetime.date(tmp.year, tmp.month, tmp.day)


class Sal(Site):
    path = os.path.join("..", os.path.join("sites_db", "sal.pickle"))
    url = "https://www.sal.tohoku.ac.jp/jp/news/covid19.html"
    base_url = "https://www.sal.tohoku.ac.jp/"
    majors = ["文学部", "文学研究科"]

    def get(self):
        soup = self.request()
        info_list = []
        permanent1 = SalNews()
        time = soup.find("p", class_="update").text
        a = re.search(r"\d+月\d+日", time)
        time = a.group()
        permanent1.content = "《{}》\n新コロナウイルス感染症（COVID-19）への対応についてが更新されました\n {}".format(
            time, self.url)
        permanent1.time = permanent1.timeobj(timestr=time)
        info_list.append(permanent1)
        return self.dic(info_list)


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

    # this should be overrided
    # because the format of news will be different from the others
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
    majors = ["教育学部", "教育学研究科"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("div", class_="inner").find_all("ul")[
            0].find_all("a")
        # 固定情報
        stick1 = SedNews(info_list[-1], self.base_url)
        stick1_url1 = "教育学研究科：https://www.sed.tohoku.ac.jp/graduate/2020class.html"
        stick1_url2 = "教育学部：https://www.sed.tohoku.ac.jp/faculty/2020class.html"
        stick1.time = stick1.timeobj(timestr="4.20")
        stick1.content = f"《4.20》\n「開講する授業の情報」が更新されることがあります。折々にご確認ください。\n{stick1_url1}\n{stick1_url2}"
        stick2 = SedNews(info_list[-1], self.base_url)
        stick2_url1 = "研究科・学部内限定：https://www2.sed.tohoku.ac.jp/computer/#compframe"
        stick2_url2 = "研究科・学部外：https://www2.sed.tohoku.ac.jp/lab/edunet/support/computer/schedule/"
        stick2.time = stick1.timeobj(timestr="4.25")
        stick2.content = f"《4.25》\nコンピュータ実習室の月間利用スケジュールを掲載\n{stick2_url1}\n{stick2_url2}"
        ###
        info_list = [SedNews(info, self.base_url) for info in self.abstract(info_list)]
        info_list.append(stick1)
        info_list.append(stick2)
        return self.dic(info_list)

    def abstract(self, tags):
        result = []
        for tag in tags:
            if tag.text not in ["「開講する授業の情報」", "研究科・学部内限定", "研究科・学部外"]:
                result.append(tag)
        return result

### 法学部・法学研究科/法科大学院・公共政策大学院 ###
class LawNews:
    def __init__(self):
        self.time = ""
        self.content = ""

    def timeobj(self, timestr=""):
        year = "2020/"
        tmp = datetime.datetime.strptime(year + timestr, "%Y/%m/%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)


class Law(Site):
    path = os.path.join("..", os.path.join("sites_db", "law.pickle"))
    url = "http://www.law.tohoku.ac.jp/covid19/"
    base_url = "http://www.law.tohoku.ac.jp"
    majors = ["法学部", "法学研究科", "法科大学院", "公共政策大学院"]

    def get(self):
        soup = self.request()
        info_list = []
        permanent1 = LawNews()
        time = soup.find(class_="law-sub-contents pos-left").find("p").text
        time = re.search(r"更新：\d+/\d+", time).group().split("更新：")[-1]
        permanent1.content = "《{}》\n新コロナウイルス感染症（COVID-19）への対応についてが更新されました\n{}".format(
            time, self.url)
        permanent1.time = permanent1.timeobj(timestr=time)
        info_list.append(permanent1)
        return self.dic(info_list)


### 経済学部・経済学研究科/会計大学院 ###
class EconNews:
    def __init__(self, data):
        self.data = data
        self.summary()

    # this should be overrided
    # because the format of news will be different from the others
    def summary(self):
        content = self.data[0]
        time = re.search(r"\d+年\d+月\d+日", self.data[1]).group()
        self.content = f"《{time}》\n{content}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        tmp = datetime.datetime.strptime(timestr, "%Y年%m月%d日")
        return datetime.date(tmp.year, tmp.month, tmp.day)


class Econ(Site):
    path = os.path.join("..", os.path.join("sites_db", "econ.pickle"))
    # ここは特例でGoogle documentやで。頑張ろうな
    url = "https://sites.google.com/view/rinji-econ-tohoku-ac-jp/"
    majors = ["経済学部", "経済学研究科", "会計大学院"]

    def get(self):
        self.url = "https://docs.google.com/document/d/19ArkoemdFSNdgeF0XQO8mI3QNhjkUbXp2lrewNGh1qQ/edit"
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        blocks = soup.find_all("script")
        for i in range(len(blocks)):
            if blocks[i].text[0:18] == "DOCS_modelChunk = ":
                block = blocks[i]
                break
        info_list = block.text.split("{")[1].split("}")[
            0].split('"')[-2].split("\\n")
        info_list = [EconNews(info) for info in self.abstract(info_list)]
        self.url = "https://sites.google.com/view/rinji-econ-tohoku-ac-jp/"
        return self.dic(info_list)

    def abstract(self, split_list):
        results = []
        count = -1
        for item in split_list:
            if item[:4] == "タイトル":
                results.append([item.split("タイトル：")[-1]])
                count += 1
            elif item[:3] == "発信日":
                results[count].append(item.split("発信日：")[-1].split("\\t")[0])
        return results


### 理学部・理学研究科 ###
class SciNews(News):
    # this should be overrided
    # because the format of news will be different from the others
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
    majors = ["理学部", "理学研究科"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        li_blocks = soup.find("ul", id="localNav").find_all("li")
        info_list1, ex = self.abstract(li_block=li_blocks[2], exception=[])
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

    # this should be overrided
    # because the format of news will be different from the others
    def summary(self):
        if self.tag.text[-1] == "）":
            time = self.tag.text.split("（")[-1].split("）")[0]
            contents = self.tag.text[:(-2 - len(time))]
        elif self.tag.text == "新型コロナウイルス感染症に関する本研究科の対応について-医学系研究科長メッセージ":
            time = "4/10"
            contents = "新型コロナウイルス感染症に関する本研究科の対応について-医学系研究科長メッセージ"
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
    majors = ["医学部", "医学系研究科"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(
            "div", class_="wrap_contarea sp_contarea area_u-layer_cont").find_all("h4")[:-1]
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

    # this should be overrided
    # because the format of news will be different from the others
    def summary(self):
        contents = self.tag.text
        time = re.search(r"\d+月\d+日", contents).group()
        href = self.tag.a.get("href")
        if href is None:
            href = "http://www.dent.tohoku.ac.jp/important/202003.html"
        elif href[:2] == "./":
            href = self.base_url + href[2:]
        elif href[0] == "#":
            href = "http://www.dent.tohoku.ac.jp/important/202003.html" + href
        self.content = f"《{time}》\n{contents.split(time)[-1]}\n{href}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        year = "2020年"
        tmp = datetime.datetime.strptime(year + timestr, "%Y年%m月%d日")
        return datetime.date(tmp.year, tmp.month, tmp.day)


class Dent(Site):
    path = os.path.join("..", os.path.join("sites_db", "dent.pickle"))
    url = "http://www.dent.tohoku.ac.jp/important/202003.html"
    base_url = "http://www.dent.tohoku.ac.jp/important"
    majors = ["歯学部", "歯学研究科"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("div", id="latest").find_all("li")
        info_list = [DentNews(info, self.base_url) for info in self.abstract(info_list)]
        return self.dic(info_list)

    def abstract(self, tags):
        result = []
        for tag in tags:
            a_tag = tag.find("a")
            if a_tag is not None:
                href = a_tag.get("href")
                if href is None:
                    result.append(tag)
                elif href[:4] != "http":
                    result.append(tag)
                elif href.split("/")[2] != "www.tohoku.ac.jp":
                    result.append(tag)
        return result


### 薬学部・薬学研究科 ###
class PharmNews(News):
    # this should be overrided
    # because the format of news will be different from the others
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
    majors = ["薬学部", "薬学研究科"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("div", class_="contents_wrap_box").find_all("a")
        info_list = self.abstract(info_list)
        # 固定情報
        stick1 = PharmNews(info_list[0])
        stick1_url = "https://www.tohoku.ac.jp/japanese/2020/04/news20200417-00.html"
        stick1.time = stick1.timeobj(timestr="4/17")
        stick1.content = f"《4/17》\n学生の入構制限について\n{stick1_url}"
        ###
        info_list = [PharmNews(info) for info in info_list]
        info_list.append(stick1)
        return self.dic(info_list)

    def abstract(self, a_tags):
        info_list = []
        for tag in a_tags:
            if tag.text not in  ["こちら", "東北大学新型コロナウイルスBCP対応ガイド", "新型コロナウイルス感染の疑いのある症状が出た場合の連絡",
                                "https://www.tohoku.ac.jp/japanese/2020/04/news20200417-00.html"]:
                href = tag.get("href")
                if (href[0:4] == "http") and (href.split("/")[2] != "www.tohoku.ac.jp"):
                    info_list.append(tag)
        return info_list


class EngENNews(News):
    def __init__(self, tag, base_url):
        '''
        <parameter>
        tag (bs4.element.Tag) : single topic object
        '''
        self.tag = tag
        self.base_url = base_url
        self.summary()

    # this should be overrided
    # because the format of news will be different from the others
    def summary(self):
        time_tag = self.tag.find_next("th")
        time_split = time_tag.text.split("/")
        print(f"time_split is {time_split}")

        # time = "{}/{}/{}".format(time_split[0], re.search(
        #     r'\d+', (time_split[1])).group())
        time = "{}/{}/{}".format(time_split[0], time_split[1], time_split[2])
        a_tag = self.tag.find("a")
        if a_tag is not None:
            href = a_tag.get("href")
            if href[0:4] != "http":
                href = self.base_url + href
            self.content = f"《{time}》\n{a_tag.text}\n{href}"
        else:
            content = "\n".join(time_tag.find_next("th").text.split())
            url = "https://www.eng.tohoku.ac.jp/english/news/news4/"
            self.content = f"《{time}》\n{content}\n{url}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        tmp = datetime.datetime.strptime(timestr, "%Y/%m/%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)


class EngEN(Site):
    path = os.path.join("..", os.path.join("sites_db", "eng.pickle"))
    url = "https://www.eng.tohoku.ac.jp/english/news/news4/"
    base_url = "https://www.eng.tohoku.ac.jp/english"
    majors = ["School of Engineering", "Graduate School of Engineering"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(class_="table nt news").find_all("tr")
        print(f"info_list is {info_list}")
        info_list = self.abstract(info_list)

        info_list = [EngENNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)

    def abstract(self, tags=[]):
        result = []
        exception = []
        for tag in tags:
            if tag.text not in exception:
                result.append(tag)
                exception.append(tag.text)
        return result


# 工学部英語
class EngENNews(News):
    def __init__(self, tag, base_url):
        '''
        <parameter>
        tag (bs4.element.Tag) : single topic object
        '''
        self.tag = tag
        self.base_url = base_url
        self.summary()

    # this should be overrided
    # because the format of news will be different from the others
    def summary(self):
        time_tag = self.tag.find_next("th")
        time_split = time_tag.text.split("/")
        print(f"time_split is {time_split}")

        # time = "{}/{}/{}".format(time_split[0], re.search(
        #     r'\d+', (time_split[1])).group())
        time = "{}/{}/{}".format(time_split[0], time_split[1], time_split[2])
        a_tag = self.tag.find("a")
        if a_tag is not None:
            href = a_tag.get("href")
            if href[0:4] != "http":
                href = self.base_url + href
            self.content = f"《{time}》\n{a_tag.text}\n{href}"
        else:
            content = "\n".join(time_tag.find_next("th").text.split())
            url = "https://www.eng.tohoku.ac.jp/english/news/news4/"
            self.content = f"《{time}》\n{content}\n{url}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        tmp = datetime.datetime.strptime(timestr, "%Y/%m/%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)


class EngEN(Site):
    path = os.path.join("..", os.path.join("sites_db", "eng.pickle"))
    url = "https://www.eng.tohoku.ac.jp/english/news/news4/"
    base_url = "https://www.eng.tohoku.ac.jp/english"
    majors = ["School of Engineering", "Graduate School of Engineering"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(class_="table nt news").find_all("tr")
        print(f"info_list is {info_list}")
        info_list = self.abstract(info_list)

        info_list = [EngENNews(info, self.base_url) for info in info_list]
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

    # this should be overrided
    # because the format of news will be different from the others
    def summary(self):
        time = re.search("\d+.\d+", self.tag.text)
        if time is not None:
            time = time.group()
            self.time = self.timeobj(time)
        else:
            time = "sample"
            self.time = time
        contents = self.tag.text.split("更新　")[-1]
        href = self.tag.get("href")
        if href[0:4] != "http":
            href = self.base_url + href
        self.content = f"《{time}》\n{contents}\n{href}"

    def timeobj(self, timestr=""):
        year = "2020."
        tmp = datetime.datetime.strptime(year + timestr, "%Y.%m.%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)


class Agri(Site):
    path = os.path.join("..", os.path.join("sites_db", "agri.pickle"))
    url = "https://www.agri.tohoku.ac.jp/jp/news/covid-19/"
    base_url = "https://www.agri.tohoku.ac.jp/jp/news/covid-19/"
    majors = ["農学部", "農学研究科"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("div", class_="area_news_cont").find_all("a")
        # 固定情報
        stick1 = AgriNews(info_list[0], self.base_url)
        contents = ["《4.13》", "農学部・農学研究科オンライン授業",
                    "https://www.agri.tohoku.ac.jp/jp/education/remote/index.html"]
        stick1.time = stick1.timeobj(timestr="4.13")
        stick1.content = "\n".join(contents)
        stick2 = AgriNews(info_list[0], self.base_url)
        contents = ["《4.13》", "東北大学オンライン授業ガイド",
                    "https://sites.google.com/view/teleclass-tohoku/forstudents"]
        stick2.time = stick1.timeobj(timestr="4.13")
        stick2.content = "\n".join(contents)
        sticks = [stick1, stick2]
        ###
        info_list = [AgriNews(info, self.url) for info in info_list]
        info_list = sticks + \
            [info for info in info_list if info.time != "sample"]
        return self.dic(info_list)


### 国際文化研究科 ###
class IntculNews(News):
    # this should be overrided
    # because the format of news will be different from the others
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
    majors = ["国際文化研究科"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
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

    # this should be overrided
    # because the format of news will be different from the others
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
    majors = ["情報科学研究科"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        info_list = []
        boxes = soup.find_all("ul", class_="border")
        for box in boxes:
            info_list.extend(box.find_all("a"))
        info_list = [ISNews(info, self.base_url) for info in info_list[:-1]]
        return self.dic(info_list)


### 生命科学研究科 ###
class LifesciNews(News):
    month_dic = {"January": "1", "Jan": "1", "February": "2", "Feb": "2", "March": "3", "Mar": "3",
                 "April": "4", "Apr": "4", "May": "5", "June": "6", "July": "7", "August": "8", "Aug": "8",
                            "September": "9", "Sept": "9", "October": "10", "Oct": "10", "November": "11", "Nov": "11",
                            "December": "12", "Dec": "12"}

    # this should be overrided
    # because the format of news will be different from the others
    def summary(self):
        content = self.tag.find("a").text
        time = self.tag.text.split(
            "(")[-1].split(" update")[0].strip("～").replace('\xa0', ' ')
        href = self.tag.find("a").get("href")
        self.content = f"《{time}》\n{content}\n{href}"
        self.time = self.timeobj(time)

    def timeobj(self, timestr=""):
        year = "2020/"
        month, day = re.split("[ .]", timestr)[:2]

        date = year + self. month_dic[month] + "/" + day
        tmp = datetime.datetime.strptime(date, "%Y/%m/%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)


class Lifesci(Site):
    path = os.path.join("..", os.path.join("sites_db", "lifesci.pickle"))
    url = "https://www.lifesci.tohoku.ac.jp/outline/covid19_taiou/"
    majors = ["生命科学研究科"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
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

    # this should be overrided
    # because the format of news will be different from the others
    def summary(self):
        time = self.tag.find("p").text.split("|")[-1].split(" ")[-1]
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
    majors = ["環境科学研究科"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [KankyoNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)


### 医工学研究科 ###
class BmeNews(News):
    # this should be overrided
    # because the format of news will be different from the others
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
    majors = ["医工学研究科"]

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("div", class_="list-news").find_all("li")
        info_list = [BmeNews(info) for info in info_list]
        return self.dic(info_list)
