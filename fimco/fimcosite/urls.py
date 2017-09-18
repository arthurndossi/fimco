from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about$', views.about, name='about'),
    url(r'^new/account', views.account, name='account'),
    url(r'^register', views.register, name='register'),
    url(r'^blog$', views.blog_view, name='blog'),
    url(r'^blog/(?P<article>[a-z-]+)', views.blog_single_view, name='blog_single'),
    url(r'^accounts/login', views.login_view, name='login'),
    url(r'^login', views.validate, name='validate'),
    url(r'^logout', views.log_out, name='logout')
]
