from queue import Queue
from django.core.management import BaseCommand

from Main.improvement import timer
from Main.improvement.crawling import Crawler, Parser

class Command(BaseCommand):

    def start_crawl(self):
        q = Queue()
        crawler = Crawler(q)
        crawler.start()
        crawler.join()
        print("Crawling end...")
        parser = Parser(q)
        parser.multi_process_parsing()
        print("Parsing end...")

    def handle(self, *args, **options):
        good_timer=timer.PeriodTimer(3600)
        good_timer.start()
        while True:
            self.start_crawl()
            good_timer.wait_for_tick()
