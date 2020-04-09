#-*- coding: utf-8 -*-
from utils import News, Site

###  ###

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
    major = "環境科学研究科"

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
    major = "医工学研究科"

    def get(self):
        soup = self.request()
        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find("div", class_="list-news").find_all("li")
        info_list = [BmeNews(info) for info in info_list]
        return self.dic(info_list)
