from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.generic.edit import FormView
from django.views.generic import ListView,DetailView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.db.models.signals import post_save
from .forms import LoginForm,RegisterForm,ChgPwdForm,ChnlForm
from .signature import token_confirm,settings
from .models import Channel,Account
import requests

# Create your views here.
def test(request):
    return  HttpResponse("Just for test")

class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm

    def form_valid(self, form):
        username=form.cleaned_data['username']
        password=form.cleaned_data['password']
        user=authenticate(username=username,password=password)
        if user is not None and user.is_active:
            login(self.request,user)
            msg='登陆成功'
            url=reverse('Main:home')
        else:
            msg='登录无效,请确认已注册激活并输入正确密码'
            url=reverse('Main:login')
        data={'message':msg,'url':url}
        return render(self.request, 'message.html', data)

class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm

    def form_valid(self, form):
        username=form.cleaned_data['username']
        email=form.cleaned_data['email']
        password=form.cleaned_data['password']
        user=User.objects.filter(username=username)
        if len(user)!=0:
            msg='该用户名已存在,请尝试其他用户名注册'
            url=reverse('Main:register')
        else:
            user=User.objects.create_user(username,email,password)
            user.is_active=False
            user.save()
            token=token_confirm.generate_validate_token(username)
            html_cont = '<p>%s,你好！欢迎注册Freader账户!请于一小时之内<a href="%s">点此链接</a>完成验证.</p>' % (username,
            '/'.join([settings.DOMAIN,'activeuser', token]))
            message=EmailMultiAlternatives('用户注册验证信息',html_cont,settings.EMAIL_HOST_USER,[email])
            message.attach_alternative(html_cont,'text/html')
            message.send()
            msg='请检查您的邮箱信息,并于一小时之内激活验证'
            url=reverse('Main:index')
        data={'message':msg,'url':url}
        return render(self.request, 'message.html', data)

def active_user_view(request,token):
    try:
        username=token_confirm.confirm_validate_token(token)
    except:
        username=token_confirm.remove_validate_token(token)
        users=User.objects.filter(username=username)
        for user in users:
            user.delete()
        msg='对不起,验证链接已经过期,请重新注册'
        url=reverse('Main:register')
        data={'message':msg,'url':url}
        return render(request, 'message.html', data)
    try:
        user=User.objects.get(username=username)
    except User.DoesNotExist:
        msg='对不起,你所验证的用户不存在,请重新注册'
        url=reverse('Main:register')
        data={'message':msg,'url':url}
        return render(request, 'message.html', data)
    user.is_active=True
    user.save()
    msg='验证成功'
    url=reverse('Main:login')
    data={'message':msg,'url':url}
    return render(request, 'message.html', data)

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    msg='退出登录'
    url=reverse('Main:index')
    data={'message':msg,'url':url}
    return render(request, 'message.html', data)

class ChgPwdView(FormView):
    template_name = 'chgpwd.html'
    form_class = ChgPwdForm

    def form_valid(self, form):
        if  not self.request.user.is_authenticated():
            msg='您还没有登录'
            url=reverse('Main:login')
        else:
            username=self.request.user.username
            old_password=form.cleaned_data['old_password']
            new_password=form.cleaned_data['new_password']
            user=authenticate(username=username,password=old_password)
            if user is None:
                msg='旧密码输入错误'
                url=reverse('Main:changepwd')
            else:
                user.set_password(new_password)
                user.save()
                msg='修改密码成功'
                url=reverse('Main:login')
        data={'message':msg,'url':url}
        return render(self.request, 'message.html', data)

@login_required(login_url='/login/')
def index_view(request):
    return redirect(reverse('Main:home'))

@receiver(post_save,sender=User)
def create_account(sender,**kwargs):
    if kwargs.get('created'):
        Account.objects.get_or_create(user=kwargs.get('instance'))

@login_required(login_url='/login/')
def addchnl_view(request):
    if 'channel' in request.POST and request.POST['channel']:
        user=request.user
        channel=request.POST['channel']
        if not 'http://' in channel and not "https://" in channel:
            channel='http://'+channel
        if len(Channel.objects.filter(link=channel))==0:
            try:
                page = requests.get(channel)
            except:
                msg = '您输入的订阅源无效,请重新输入'
                url = reverse('Main:home')
                data = {'message': msg, 'url': url}
                return render(request,'message.html',data)
            channel=Channel(link=channel)
            channel.save()
            msg='订阅成功'
        elif len(user.account.channel.filter(link=channel))>0:
            msg='您已经订阅过啦'
        else:
            channel=Channel.objects.get(link=channel)
            user.account.channel.add(channel)
            msg='订阅成功'
        url=reverse('Main:home')
        data={'message':msg,'url':url}
        return render(request,'message.html',data)
    else:
        url=reverse('Main:home')
        return redirect(url)

class HomePageView(ListView):
    template_name = 'homepage.html'
    context_object_name = 'channel_list'

    def get_queryset(self):
        user=self.request.user
        if not user.is_anonymous:
            channel_list=user.account.channel.all().distinct()
            return channel_list
        else:
            return None

    def get_context_data(self, **kwargs):
        if self.request.user.is_anonymous():
            kwargs['username']='游客'
        else:
            kwargs['username']=self.request.user.username
        kwargs['form']=ChnlForm()
        return super(HomePageView,self).get_context_data(**kwargs)

class ChnlUpdtView(DetailView):
    model = Channel
    template_name = 'chnlupdt.html'
    context_object_name = 'channel'
    pk_url_kwarg = 'chnl_id'

    def get_context_data(self, **kwargs):
        kwargs['items']=self.object.item_set.all().distinct()
        if self.request.user.is_anonymous:
            kwargs['username']='游客'
        else:
            kwargs['username']=self.request.user.username
        return super(ChnlUpdtView,self).get_context_data(**kwargs)

@login_required(login_url='/login/')
def delchnl_view(request,chnl_id):
    user=request.user
    channel=Channel.objects.get(id=int(chnl_id))
    user.account.channel.remove(channel)
    msg='删除成功'
    url=reverse('Main:home')
    data={'message':msg,'url':url}
    return render(request, 'message.html', data)
