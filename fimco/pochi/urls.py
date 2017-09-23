from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^dashboard$', views.admin, name='pochi'),
    url(r'^dashboard$', views.admin, name='dashboard'),
    url(r'^statements$', views.statements, name='statements'),
    url(r'^statement-print$', TemplateView.as_view(template_name='statement-print.html'), name='printout'),
    url(r'^pochi2pochi$', views.pochi2pochi, name='pochi2pochi'),
    url(r'^withdrawal$', views.withdrawal, name='withdrawal'),
    url(r'^deposit$', views.deposit, name='deposit'),
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
    url(r'^stocks$', views.stocks, name='stocks')
]
