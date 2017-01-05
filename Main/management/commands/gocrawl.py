import multiprocessing
import threading
from queue import Queue

import time
from django.core.management import BaseCommand

from Main.improvement import timer
from Main.improvement.crawling import Crawler, Parser
from multiprocessing.managers import BaseManager

from Main.improvement.master import Master
from Main.improvement import slave0,slave1


class Command(BaseCommand):

    def start_crawl(self):
        q = Queue()
        crawler = Crawler(q,10)
        parser = Parser(q, 10)
        #crawler.multi_threaded_crawling()
        crawler.async_coroutine_crawling()
        parser.multi_process_parsing()
        crawler.async_wait_for_end()
        #crawler.wait_for_end()
        parser.wait_for_end()

    def multi_queue_crawl(self):
        master=Master()
        slave_0=slave0.Slave(10,10)
        slave_1=slave1.Slave(10,10)
        master.task_schedule()
        #slave_0.start()
        #slave_1.start()
        s0_thread=threading.Thread(target=slave_0.start)
        s1_thread=threading.Thread(target=slave_1.start)
        s0_thread.start()
        s1_thread.start()
        master.wait_for_other_hosts()
        time.sleep(600)
        slave_0.wait_for_end()
        slave_1.wait_for_end()

    def handle(self, *args, **options):
        good_timer=timer.PeriodTimer(3600)
        good_timer.start()
        while True:
            #self.start_crawl()
            self.multi_queue_crawl()
            good_timer.wait_for_tick()
