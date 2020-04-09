#-*- coding: utf-8 -*-
from utils import News, Site


### 全体 ###
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

class TU(Site):
    path = "../sites_db/tu.pickle"
    url = "http://www.tohoku.ac.jp/japanese/disaster/outbreak/01/outbreak0101/"
    base_url = "http://www.tohoku.ac.jp"
    major = ["全体"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [TUNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)


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
    path = "../sites_db/sal.pickle"
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
    path = "../sites_db/sed.pickle"
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
    path = "../sites_db/law.pickle"
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
    path = "../sites_db/econ.pickle"
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

class Sci(Site):
    path = "../sites_db/sci.pickle"
    url = "https://www.sci.tohoku.ac.jp/news/20200305-10978.html"
    base_url = "https://www.sci.tohoku.ac.jp"
    major = ["理学部", "理学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [SciNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)


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
    path = "../sites_db/med.pickle"
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

class Dent(Site):
    path = "../sites_db/dent.pickle"
    url = "http://www.dent.tohoku.ac.jp/important/202003.html"
    base_url = "http://www.dent.tohoku.ac.jp"
    major = ["歯学部", "歯学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [DentNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)


### 薬学部・薬学研究科 ###
class PharmNews(News):
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

class Pharm(Site):
    path = "../sites_db/pharm.pickle"
    url = "http://www.pharm.tohoku.ac.jp/info/200331/200331.shtml"
    base_url = "http://www.pharm.tohoku.ac.jp"
    major = ["薬学部", "薬学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find(id="news-article-single").find_all("li")
        info_list = [PharmNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)


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
    path = "../sites_db/eng.pickle"
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
    path = "../sites_db/agri.pickle"
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
    path = "../sites_db/intcul.pickle"
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
    path = "../sites_db/is.pickle"
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
    path = "../sites_db/lifesci.pickle"
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
    path = "../sites_db/kankyo.pickle"
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
    path = "../sites_db/bme.pickle"
    url = "http://www.bme.tohoku.ac.jp/information/news/"
    major = ["医工学研究科"]

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("div", class_="list-news").find_all("li")
        info_list = [BmeNews(info) for info in info_list]
        return self.dic(info_list)
