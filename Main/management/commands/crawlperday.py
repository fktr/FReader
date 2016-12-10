import feedparser
import requests
from django.core.management import BaseCommand

from Main.models import Channel, Item
from Main.util.easy import pubdate_to_datetime, get_htmlcont, beautify_data


class Command(BaseCommand):

    def handle(self, *args, **options):
        channels = Channel.objects.all().distinct()
        for channel in channels:
            content=get_htmlcont(channel.link)
            parsed_cont = feedparser.parse(content)
            channel.title = parsed_cont.feed.get('title', '暂无标题')
            channel.description = parsed_cont.feed.get('description', '暂无描述')
            print('Crawling Channel %s' % channel.title)
            has_update=False
            for entry in parsed_cont.entries:
                item_link = entry.get('link', '暂无链接')
                item_pubdate = entry.get('published', '暂无发布日期')
                item_pubdate=pubdate_to_datetime(item_pubdate)
                is_new=False
                if channel.item_set.filter(channel__item__link=item_link, channel__item__pubdate=item_pubdate):
                    continue
                item_title = entry.get('title', '暂无标题')
                item_description = entry.get('description', '暂无描述')
                item_description=beautify_data(item_description)
                is_new=True
                item = Item(title=item_title, description=item_description, link=item_link, pubdate=item_pubdate,
                            channel=channel,is_new=is_new)
                item.save()
                print('Find Item %s' % item.title)
                has_update=True
            channel.has_update=has_update
            channel.save()

