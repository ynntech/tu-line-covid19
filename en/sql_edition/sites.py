# -*- coding: utf-8 -*-
import os
import re
import datetime

from utils import News, Site


### 全学生向け ###
class BcpEnNews:
    def __init__(self, tag, base_url):
        self.tag = tag
        self.base_url = base_url
        self.summary()

    # this should be overrided
    # because the format of news will be different from the others
    def summary(self):
        thumbnail = self.tag.find("img").get("src")
        if thumbnail[:4] != "http":
            thumbnail = self.base_url + thumbnail
        time = self.tag.find("div", class_="date").text
        contents = self.tag.find("div", class_="headline").find("a")
        href = contents.get("href")
        if href[:4] != "http":
            href = self.base_url + href
        self.content = f"《{time}》\n{contents.text}\n{href}"
        self.time = self.timeobj(time)
        self.thumbnail = thumbnail

    def timeobj(self, timestr=""):
        tmp = datetime.datetime.strptime(timestr, "%Y-%m-%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)

class BcpEn(Site):
    url = "https://www.tohoku.ac.jp/en/news/university_news/index.html"
    base_url = "https://www.tohoku.ac.jp"
    table = "TU"

    def get(self):
        soup = self.request()
        # 以降、サイトに合わせて書き直す必要あり
        box = soup.find("div", class_="eventsIndex")
        info_list = box.find_all("li")
        info_list = [BCPNews(info, self.base_url) for info in info_list]
        return self.dic(info_list)


### 工学部英語版 ###
class EngEnNews(News):
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


class EngEn(Site):
    path = os.path.join("..", os.path.join("sites_db", "eng.pickle"))
    url = "https://www.eng.tohoku.ac.jp/english/news/news4/"
    base_url = "https://www.eng.tohoku.ac.jp/english"
    table = "ENGINEER"

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
