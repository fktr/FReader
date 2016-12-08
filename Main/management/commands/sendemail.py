from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.management import BaseCommand

from FReader import settings
from Main.models import Channel, Item, Account


class Command(BaseCommand):

    def handle(self, *args, **options):
        accounts=Account.objects.all().distinct()
        for account in accounts:
            update_cont={}
            channels=account.channel.filter(has_update=True)
            for channel in channels:
                print('%s %s' %(channel.title,account.user.username))
                update_num=len(channel.item_set.filter(is_new=True))
                update_cont[channel.title]=update_num
            if len(update_cont)>0:
                mail_cont='<h>亲爱的%s,您的订阅有更新啦!</h><h3>具体如下:</h3><div><ul>' % account.user.username
                for key,value in update_cont.items():
                    mail_cont+='<li>%s 有 %d 条更新.</li>' %(key,value)
                mail_cont+='</ul></div>'
                message = EmailMultiAlternatives('订阅更新通知', mail_cont, settings.EMAIL_HOST_USER, [account.user.email])
                message.attach_alternative(mail_cont, 'text/html')
                message.send()
                print('Send Email To %s' % account.user.username)
        channels=Channel.objects.all().filter(has_update=True)
        for channel in channels:
            channel.has_update=False
            channel.save()
        items=Item.objects.all().filter(is_new=True)
        for item in items:
            item.is_new=False
            item.save()
