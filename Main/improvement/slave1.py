import asyncio
import multiprocessing
import queue
import re

import aiohttp
import feedparser
import requests
import threadpool
from multiprocessing.managers import BaseManager

from Main.models import Item
from Main.util.easy import pubdate_to_datetime, beautify_data

BaseManager.register('get_task_queue_1')
BaseManager.register('get_result_queue_1')
server_addr='127.0.0.1'
manager=BaseManager(address=(server_addr,5000),authkey=b'haha')
manager.connect()

class Slave:

    def __init__(self,t_num,p_num):
        self.taskq=manager.get_task_queue_1()
        self.resultq=manager.get_result_queue_1()
        self.bufferq=queue.Queue()
        self.thread_num=t_num
        self.process_num=p_num
        self.thread_pool=threadpool.ThreadPool(self.thread_num)
        self.process_pool=multiprocessing.Pool(self.process_num)
        self.event_loop=asyncio.get_event_loop()

    def crawl_page(self,channel):
        print('@Function :crawl_page')
        headers = {'User-Agent': 'user-agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'}
        page = requests.get(url=channel.link, headers=headers)
        coding_pattern = re.compile(r'encoding=(?P<coding>[\w-]*)?>')
        page_coding = re.search(coding_pattern, page.text)
        page.encoding = page_coding
        self.bufferq.put((channel,page.text))
        print('@Host1 Put task %s into buffer queue...'%channel)

    async def async_crawl(self,channel):
        print('@Function :async_crawl')
        headers = {'User-Agent': 'user-agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'}
        async with aiohttp.ClientSession() as session:
            async with session.get(url=channel.link,headers=headers) as resp:
                self.bufferq.put((channel,await resp.text()))
                print('@Host1 Put task %s into buffer queue...'%channel)

    def multi_threaded_crawling(self):
        print("Crawling begin...")
        channels=[]
        while True:
            try:
                channel=self.taskq.get(timeout=60)
                #self.taskq.task_done()
                print('@Host1 Get task %s from task queue...' % channel)
                channels.append(channel)
            except:
                break
        tasks=threadpool.makeRequests(self.crawl_page,channels)
        for task in tasks:
            self.thread_pool.putRequest(task)

    def async_coroutine_crawling(self):
        print('Async Crawling begin...')
        channels = []
        while True:
            try:
                channel = self.taskq.get(timeout=60)
                #self.taskq.task_done()
                print('@Host1 Get task %s from task queue...' % channel)
                channels.append(channel)
            except:
                break
        tasks=[self.async_crawl(channel) for channel in channels]
        self.event_loop.run_until_complete(asyncio.wait(tasks))

    def multi_process_parsing(self):
        print("Parsing begin...")
        while True:
            try:
                channel,page_cont = self.bufferq.get(timeout=300)
                print('@Host1 Get task %s from buffer queue...'%channel)
                #print(page_cont[:100])
                #self.bufferq.task_done()
                self.process_pool.apply_async(parse_page,(channel,page_cont))
            except:
                break

    def start(self):
        self.multi_threaded_crawling()
        self.multi_process_parsing()

    def wait_for_end(self):
        print('@Function: wait_for_end')
        #self.taskq.join()
        #self.bufferq.join()
        self.thread_pool.wait()
        print("@Host1 Crawling end...")
        self.process_pool.close()
        self.process_pool.join()
        print("@Host1 Parsing end...")

    def async_wait_for_end(self):
        print('@Function: async_wait_for_end')
        #self.taskq.join()
        #self.bufferq.join()
        self.event_loop.close()
        print('@Host1 Async Crawling end...')
        self.process_pool.close()
        self.process_pool.join()
        print("@Host1 Parsing end...")


def parse_page(channel, page_cont):
    print('@Function: parse_page')
    parsed_cont = feedparser.parse(page_cont)
    channel.title = parsed_cont.feed.get('title', '暂无标题')
    channel.description = parsed_cont.feed.get('description', '暂无描述')
    print('Crawling Channel %s' % channel.title)
    has_update = False
    result=[]
    result.append(channel)
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
        #item.save()
        result.append(item)
        print('Find Item %s' % item.title)
        has_update = True
    #channel.has_update=has_update
    #channel.save()
    result[0].has_update=has_update
    resultq=manager.get_result_queue_1()
    resultq.put(result)
    print('@Host1 Put result %s into result queue...'%result[0])
