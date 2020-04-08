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

    ## this should be overrided
    ## because the format of news will be different from the others
    def summary(self):
        self.time = self.tag.find("th").text
        a_tags = self.tag.find_all("a")
        contents = []
        links = []
        for i in range(len(a_tags)):
            href = a_tags[i].get("href")
            if href[0] == "/":
                href = self.base_url + href
            links.append(href)
            contents.append(a_tags[i].text)
        self.link_list = links
        self.content = "\n".join([self.time, "\n".join(contents), "\n".join(links)])

class Site:
    def __init__(self, url, base_url=None):
        ## http://www.intcul.tohoku.ac.jp/
        self.url = url
        self.base_url = base_url

    def get(self):
        response =  requests.get(self.url)
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, "lxml")

        ## 以降、サイトに合わせて書き直す必要あり
        info_list = soup.find_all("tr")
        info_list = Monitor(info_list, self.base_url)
        info_list.summary()

if __name__ == "__main__":
    intcul = Site("http://www.intcul.tohoku.ac.jp/")
    intcul.get()
