from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Channel(models.Model):
    title=models.CharField('标题',max_length=32)
    link=models.CharField('订阅源',max_length=64)
    description=models.CharField('描述',max_length=128)
    created_time=models.DateTimeField("创建时间",auto_now_add=True)

    def __str__(self):
        return self.title

class Item(models.Model):
    title=models.CharField('标题',max_length=32)
    link=models.CharField('链接',max_length=64)
    pubdate=models.CharField('发布时间',max_length=32)
    description=models.CharField('描述',max_length=128)
    channel=models.ForeignKey(Channel,verbose_name='所属源')

    def __str__(self):
        return self.title

class Account(models.Model):
    user=models.OneToOneField(User,verbose_name='用户')
    channel=models.ManyToManyField(Channel,verbose_name='订阅收藏')

    def __str__(self):
        return self.user.username
