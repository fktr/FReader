from django.core.management import BaseCommand
from Main.models import Channel

'''

'''

rss_group=[
    'https://www.zhihu.com/rss',
    'http://today.hit.edu.cn/rss.xml',
    'http://www.nhzy.org/feed',
    'http://www.matrix67.com/blog/feed',
    'https://bbs.sjtu.edu.cn/bbsrss?board=SJTUNews',
    'http://www.geekpark.net/feed',
    'http://www.alibuybuy.com/feed',
    'http://www.u148.net/rss/',
]

class Command(BaseCommand):

    def handle(self, *args, **options):
        Channel.objects.all().delete()
        for rss in rss_group:
            channel=Channel(link=rss)
            channel.save()

