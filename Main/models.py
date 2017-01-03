from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.utils import timezone


class Channel(models.Model):
    title=models.CharField('标题',max_length=32)
    link=models.CharField('订阅源',max_length=64)
    description=models.CharField('描述',max_length=128)
    created_time=models.DateTimeField("创建时间",auto_now_add=True)
    has_update=models.BooleanField('是否有更新',default=False)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return self.link

    class Meta:
        ordering=['-created_time']

class Item(models.Model):
    title=models.CharField('标题',max_length=32)
    link=models.CharField('链接',max_length=64)
    pubdate=models.DateTimeField('发布时间',null=True)
    description=models.CharField('描述',max_length=128)
    channel=models.ForeignKey(Channel,verbose_name='所属源')
    is_new=models.BooleanField('是否是最新',default=False)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return self.link

    class Meta:
        ordering=['-pubdate']

class Account(models.Model):
    user=models.OneToOneField(User,verbose_name='用户')
    channel=models.ManyToManyField(Channel,verbose_name='订阅收藏')

    def __str__(self):
        return self.user.username
