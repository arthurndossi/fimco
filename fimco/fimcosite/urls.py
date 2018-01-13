from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new/account$', views.RegistrationWizard.as_view(), name='account'),
    url(r'^corporate/account$', views.CorporateWizard.as_view(), name='corporate'),
    url(r'^corporate/add/user$', views.add_user_corporate, name='add_user'),
    url(r'^register$', views.register, name='register'),
    url(r'^site/(?P<page>[a-z-]+)$', views.general_view, name='site'),
    url(r'^blog/(?P<article>[a-z-]+)$', views.blog_single_view, name='blog_single'),
    url(r'^information/(?P<page>[a-z-]+)$', views.info, name='info'),
    url(r'^site/contact/inquiry$', views.inquiry, name='inquiry'),
    url(r'^accounts/login', views.login_view, name='login'),
    url(r'^login', views.validate, name='validate'),
    url(r'^logout', views.log_out, name='logout'),
]
