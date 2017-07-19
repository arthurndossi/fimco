from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about$', views.about, name='about'),
    url(r'^services$', views.services, name='services'),
    url(r'^blog$', views.blog, name='blog'),
    url(r'^clients$', views.clients, name='clients'),
    url(r'^contact-us$', views.contact, name='contact'),
    url(r'^account', views.register, name='account'),
]
