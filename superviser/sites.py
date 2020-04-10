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
        self.time = self.tag.find("p").text.split(" | ")[-1]
        a_tags = self.tag.find_all("a")
        contents = "".join(self.tag.text.split(" | " + self.time))
        links = []
        for i in range(len(a_tags)):
            href = a_tags[i].get("href")
            links.append(href)
        self.content = contents + "\n".join(links)

class Sal(Site):
    path = os.path.join("..", os.path.join("sites_db", "sal.pickle"))
    url = "https://www.sal.tohoku.ac.jp/"
    major = ["文学部", "文学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [SalNews(info) for info in info_list]
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

    ## this should be overrided
    ## because the format of news will be different from the others
    def summary(self):
        self.time = self.tag.find("p").text.split(" | ")[-1]
        a_tags = self.tag.find_all("a")
        contents = "".join(self.tag.text.split(" | " + self.time))
        links = []
        for i in range(len(a_tags)):
            href = a_tags[i].get("href")
            if href[0:4] != "http":
                href = self.base_url + href
            links.append(href)
        self.content = contents + "\n".join(links)

class Sed(Site):
    path = os.path.join("..", os.path.join("sites_db", "sed.pickle"))
    url = "https://www.sed.tohoku.ac.jp/news.html"
    base_url = "https://www.sed.tohoku.ac.jp"
    major = ["教育学部", "教育学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [SedNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)


### 法学部・法学研究科 ###
class LawNews(News):
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
        self.time = self.tag.find("p").text.split(" | ")[-1]
        a_tags = self.tag.find_all("a")
        contents = "".join(self.tag.text.split(" | " + self.time))
        links = []
        for i in range(len(a_tags)):
            href = a_tags[i].get("href")
            if href[0:4] != "http":
                href = self.base_url + href
            links.append(href)
        self.content = contents + "\n".join(links)

class Law(Site):
    path = os.path.join("..", os.path.join("sites_db", "law.pickle"))
    url = "http://www.law.tohoku.ac.jp/covid19/"
    base_url = "http://www.law.tohoku.ac.jp"
    major = ["法学部", "法学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [LawNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)


### 経済学部・経済学研究科 ###
class EconNews(News):
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
        self.time = self.tag.find("p").text.split(" | ")[-1]
        a_tags = self.tag.find_all("a")
        contents = "".join(self.tag.text.split(" | " + self.time))
        links = []
        for i in range(len(a_tags)):
            href = a_tags[i].get("href")
            links.append(href)
        self.content = contents + "\n".join(links)

class Econ(Site):
    path = os.path.join("..", os.path.join("sites_db", "econ.pickle"))
    url = "https://sites.google.com/view/rinji-econ-tohoku-ac-jp/"
    major = ["経済学部", "経済学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [EconNews(info) for info in info_list]
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
        self.time = self.tag.find("p").text.split(" | ")[-1]
        a_tags = self.tag.find_all("a")
        contents = "".join(self.tag.text.split(" | " + self.time))
        links = []
        for i in range(len(a_tags)):
            href = a_tags[i].get("href")
            if href[0:4] != "http":
                href = self.base_url + href
            links.append(href)
        self.content = contents + "\n".join(links)

class Med(Site):
    path = os.path.join("..", os.path.join("sites_db", "med.pickle"))
    url = "https://www.med.tohoku.ac.jp/admissions/2003announce/index.html#cst3"
    base_url = "https://www.med.tohoku.ac.jp"
    major = ["医学部", "医学系研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [MedNews(info, self.base_url) for info in info_list]
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
        self.time = self.tag.find("p").text.split(" | ")[-1]
        a_tags = self.tag.find_all("a")
        contents = "".join(self.tag.text.split(" | " + self.time))
        links = []
        for i in range(len(a_tags)):
            href = a_tags[i].get("href")
            if href[0:4] != "http":
                href = self.base_url + href
            links.append(href)
        self.content = contents + "\n".join(links)

class Eng(Site):
    path = os.path.join("..", os.path.join("sites_db", "eng.pickle"))
    url = "https://www.eng.tohoku.ac.jp/news/detail-,-id,1561.html"
    base_url = "https://www.eng.tohoku.ac.jp"
    major = ["工学部", "工学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [EngNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)


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
        self.time = self.tag.find("p").text.split(" | ")[-1]
        a_tags = self.tag.find_all("a")
        contents = "".join(self.tag.text.split(" | " + self.time))
        links = []
        for i in range(len(a_tags)):
            href = a_tags[i].get("href")
            if href[0:4] != "http":
                href = self.base_url + href
            links.append(href)
        self.content = contents + "\n".join(links)

class Agri(Site):
    path = os.path.join("..", os.path.join("sites_db", "agri.pickle"))
    url = "https://www.agri.tohoku.ac.jp/jp/news/covid-19/"
    base_url = "https://www.agri.tohoku.ac.jp"
    major = ["農学部", "農学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [AgriNews(info, self.base_url) for info in info_list]
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
        self.time = self.tag.find("p").text.split(" | ")[-1]
        a_tags = self.tag.find_all("a")
        contents = "".join(self.tag.text.split(" | " + self.time))
        links = []
        for i in range(len(a_tags)):
            href = a_tags[i].get("href")
            links.append(href)
        self.content = contents + "\n".join(links)

class Intcul(Site):
    path = os.path.join("..", os.path.join("sites_db", "intcul.pickle"))
    url = "http://www.intcul.tohoku.ac.jp/"
    major = ["国際文化研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
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
        self.time = self.tag.find("p").text.split(" | ")[-1]
        a_tags = self.tag.find_all("a")
        contents = "".join(self.tag.text.split(" | " + self.time))
        links = []
        for i in range(len(a_tags)):
            href = a_tags[i].get("href")
            if href[0:4] != "http":
                href = self.base_url + href
            links.append(href)
        self.content = contents + "\n".join(links)

class IS(Site):
    path = os.path.join("..", os.path.join("sites_db", "is.pickle"))
    url = "https://www.is.tohoku.ac.jp/jp/forstudents/detail---id-2986.html"
    base_url = "https://www.is.tohoku.ac.jp"
    major = ["情報科学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [ISNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)


### 生命科学研究科 ###
class LifesciNews(News):
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
        self.time = self.tag.find("p").text.split(" | ")[-1]
        a_tags = self.tag.find_all("a")
        contents = "".join(self.tag.text.split(" | " + self.time))
        links = []
        for i in range(len(a_tags)):
            href = a_tags[i].get("href")
            if href[0:4] != "http":
                href = self.base_url + href
            links.append(href)
        self.content = contents + "\n".join(links)

class Lifesci(Site):
    path = os.path.join("..", os.path.join("sites_db", "lifesci.pickle"))
    url = "https://www.lifesci.tohoku.ac.jp/outline/covid19_taiou/"
    base_url = "https://www.lifesci.tohoku.ac.jp"
    major = ["生命科学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [LifesciNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)


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
        self.time = self.tag.find("p").text.split(" | ")[-1]
        a_tags = self.tag.find_all("a")
        contents = "".join(self.tag.text.split(" | " + self.time))
        links = []
        for i in range(len(a_tags)):
            href = a_tags[i].get("href")
            if href[0:4] != "http":
                href = self.base_url + href
            links.append(href)
        self.content = contents + "\n".join(links)

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
        self.time = time
        self.content = " ".join(contents) + "\n" + "\n".join(links)

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
