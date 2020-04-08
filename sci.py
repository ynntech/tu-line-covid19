import requests
from bs4 import BeautifulSoup


class Monitor:
    def __init__(self, target, base_url):
        '''
        <parameter>
        target (list) : list of bs4.element.Tag objects
        '''
        self.target = [News(topic, base_url) for topic in target]
        self.base_url = base_url
        self.count = len(target)

    def summary(self):
        for i in range(self.count):
            print(self.target[i].content)


class News:
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
        contents = self.tag.text.split()
        self.time = "/".join(contents[0].split("."))
        hrefs = [a.get("href") for a in self.tag.find_all("a")]
        for i in range(len(hrefs)):
            if hrefs[i][0] == "/":
                hrefs[i] = self.base_url + hrefs[i]
        self.link_list = hrefs
        self.content = "\n".join([self.time, " ".join(
            contents[2:]), "\n".join(self.link_list)])


class Site:
    def __init__(self, url, base_url, tag, class_name):
        # https://www.eng.tohoku.ac.jp/news/detail-,-id,1561.html#1
        self.url = url
        # https://www.eng.tohoku.ac.jp/
        self.base_url = base_url
        self.tag = tag
        self.class_name = class_name

    def get(self):
        response = requests.get(self.url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "lxml")

        # 以降、サイトに合わせて書き直す必要あり
        boxes = soup.find_all(self.tag, class_=self.class_name)
        # ===============================
        # ここから、各学科ごとにメソッドでわける。
        # 「4月入学者のみなさまへ」はindex 1
        box = boxes[1]
        info_list = box.find_all("li")
        for_freshmen = Monitor(info_list, self.base_url)
        for_freshmen.summary()


if __name__ == "__main__":
    sci = Site("https://www.sci.tohoku.ac.jp/news/20200305-10978.html",
               "https://www.sci.tohoku.ac.jp/", "ul", "localNav")
    sci.get()
