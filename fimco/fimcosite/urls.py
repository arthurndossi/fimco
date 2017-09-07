from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about$', views.about, name='about'),
    url(r'^invest', views.account, name='invest'),
    url(r'^register', views.register, name='register'),
    url(r'^accounts/login', views.login, name='login'),
    url(r'^logout', views.log_out, name='logout')
]
