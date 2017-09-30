from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about$', views.about, name='about'),
    url(r'^new/account$', views.account, name='account'),
    url(r'^register$', views.register, name='register'),
    url(r'^edit/user$', views.view_profile, name='edit'),
    url(r'^profile$', views.edit_profile, name='profile'),
    url(r'^blog$', views.blog_view, name='blog'),
    url(r'^fund$', views.fund, name='fund'),
    url(r'^brokerage$', views.brokerage, name='brokerage'),
    url(r'^blog/(?P<article>[a-z-]+)$', views.blog_single_view, name='blog_single'),
    url(r'^information/pochi', views.info, name='info'),
    url(r'^accounts/login$', views.login_view, name='login'),
    url(r'^login', views.validate, name='validate'),
    url(r'^logout', views.log_out, name='logout'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^terms&conditions$', views.terms, name='terms')
]
