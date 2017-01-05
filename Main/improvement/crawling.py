import asyncio
import multiprocessing
import re
import aiohttp
import feedparser
import requests
import threadpool
from Main.models import Channel, Item
from Main.util.easy import  pubdate_to_datetime, beautify_data

class Crawler:

    def __init__(self,out_q,t_num):
        self.queue=out_q
        self.thread_num=t_num
        self.channels=Channel.objects.all().distinct()
        self.pool=threadpool.ThreadPool(self.thread_num)
        self.loop=asyncio.get_event_loop()

    def crawl_page(self,channel):
        headers = {'User-Agent': 'user-agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'}
        page = requests.get(url=channel.link, headers=headers)
        coding_pattern = re.compile(r'encoding=(?P<coding>[\w-]*)?>')
        page_coding = re.search(coding_pattern, page.text)
        page.encoding = page_coding
        self.queue.put((channel,page.text))

    async def async_crawl(self,channel):
        headers = {'User-Agent': 'user-agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'}
        async with aiohttp.ClientSession() as session:
            async with session.get(url=channel.link,headers=headers) as resp:
                self.queue.put((channel,await resp.text()))

    def multi_threaded_crawling(self):
        print("Crawling begin...")
        tasks=threadpool.makeRequests(self.crawl_page,self.channels)
        for task in tasks:
            self.pool.putRequest(task)

    def async_coroutine_crawling(self):
        print('Async Crawling begin...')
        tasks=[self.async_crawl(channel) for channel in self.channels]
        self.loop.run_until_complete(asyncio.wait(tasks))

    def wait_for_end(self):
        self.pool.wait()
        print("Crawling end...")

    def async_wait_for_end(self):
        self.loop.close()
        print('Async Crawling end...')


class Parser:

    def __init__(self,in_q,p_num):
        self.queue=in_q
        self.process_num=p_num
        self.pool = multiprocessing.Pool(self.process_num)

    def multi_process_parsing(self):
        print("Parsing begin...")

        while True:
            try:
                channel,page_cont = self.queue.get(timeout=600)
                self.pool.apply_async(parse_page,(channel,page_cont))
            except:
                break

    def wait_for_end(self):
        self.pool.close()
        self.pool.join()
        print("Parsing end...")


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
