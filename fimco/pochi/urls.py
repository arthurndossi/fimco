from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^dashboard$', views.admin, name='pochi'),
    url(r'^markets$', views.markets, name='markets'),
    url(r'^exchange', views.exchange_rates, name='exchange'),
    url(r'^interests$', views.interest_rates, name='interests'),
    url(r'^share$', views.share_prices, name='share'),
    url(r'^macro$', views.macro_data, name='macro'),
    url(r'^auction$', views.auction_data, name='auction'),
    url(r'^commodities$', views.commodity_prices, name='commodities'),
    url(r'^messages$', views.notifications, name='messages'),
    url(r'^profile$', views.edit_profile, name='profile'),
    url(r'^lock$', views.lock, name='lock'),
    url(r'^rates$', views.rates, name='rates'),
]
