from django.conf.urls import url
from .views import *

urlpatterns=[
    url(r'^$',index_view,name='index'),
    url(r'^home/$',HomePageView.as_view(),name='home'),
    url(r'^chnl/(?P<chnl_id>\d+)/$',ChnlUpdtView.as_view(),name='chnlupdt'),
    url(r'^addchnl/$',addchnl_view,name='addchnl'),
    url(r'^delchnl/(?P<chnl_id>\d+)/$',delchnl_view,name='delchnl'),
    url(r'^login/$',LoginView.as_view(),name='login'),
    url(r'^register/$',RegisterView.as_view(),name='register'),
    url(r'^chgpwd/$',ChgPwdView.as_view(),name='chgpwd'),
    url(r'^logout/$',logout_view,name='logout'),
    url(r'^activeuser/(?P<token>\w+.[-_\w]*\w+.[-_\w]*\w+)/$', active_user_view, name='activeuser'),
]
