from django.conf.urls import url

from . import views

urlpatterns = [
   url(r'^(?P<page>[a-zA-Z]+)/$', views.market_views, name='page'),
#    url(r'^markets$', views.market, name='markets'),
   url(r'^exchange/(?P<page>[a-zA-Z]+)/$', views.exchange_view, name='exchange'),
   url(r'^interests$', views.interests_view, name='interests'),
#    url(r'^share$', views.share_prices, name='share'),
#    url(r'^macro$', views.macro_data, name='macro'),
#    url(r'^auction$', views.auction_data, name='auction'),
#    url(r'^commodities$', views.commodity_prices, name='commodities'),
#    url(r'^stocks$', views.stocks, name='stocks'),
#    url(r'^rates$', views.rates, name='rates')
]