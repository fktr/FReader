import multiprocessing
import re
import feedparser
import threading
import requests
from Main.models import Channel, Item
from Main.util.easy import  pubdate_to_datetime, beautify_data

class Crawler(threading.Thread):

    def __init__(self,out_q):
        super().__init__()
        self.queue=out_q
        self.channels=Channel.objects.all().distinct()
        self.qlist=[]

    def crawl_page(self,channel):
        headers = {'User-Agent': 'user-agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'}
        page = requests.get(url=channel.link, headers=headers)
        coding_pattern = re.compile(r'encoding=(?P<coding>[\w-]*)?>')
        page_coding = re.search(coding_pattern, page.text)
        page.encoding = page_coding
        self.queue.put((channel,page.text))

    def run(self):
        print("Crawling begin...")
        for channel in self.channels:
            thread=threading.Thread(target=self.crawl_page,args=(channel,))
            thread.start()
            self.qlist.append(thread)
        for thread in self.qlist:
            thread.join()

class Parser:

    def __init__(self,in_q):
        self.queue=in_q

    def multi_process_parsing(self):
        print("Parsing begin")
        pool=multiprocessing.Pool(10)
        while not self.queue.empty():
            channel,page_cont = self.queue.get()
            pool.apply_async(parse_page,(channel,page_cont))
        pool.close()
        pool.join()

def parse_page(channel, page_cont):
    parsed_cont = feedparser.parse(page_cont)
    channel.title = parsed_cont.feed.get('title', '暂无标题')
    channel.description = parsed_cont.feed.get('description', '暂无描述')
    print('Crawling Channel %s' % channel.title)
    has_update = False
    for entry in parsed_cont.entries:
        item_link = entry.get('link', '暂无链接')
        item_pubdate = entry.get('published', '暂无发布日期')
        item_pubdate = pubdate_to_datetime(item_pubdate)
        is_new = False
        if channel.item_set.filter(channel__item__link=item_link, channel__item__pubdate=item_pubdate):
            continue
        item_title = entry.get('title', '暂无标题')
        item_description = entry.get('description', '暂无描述')
        item_description = beautify_data(item_description)
        is_new = True
        item = Item(title=item_title, description=item_description, link=item_link, pubdate=item_pubdate,
                    channel=channel, is_new=is_new)
        item.save()
        print('Find Item %s' % item.title)
        has_update = True
    channel.has_update = has_update
    channel.save()
