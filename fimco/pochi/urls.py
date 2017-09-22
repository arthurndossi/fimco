from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^app$', views.admin, name='pochi'),
    url(r'^dashboard$', views.dashboard, name='dashboard'),
    url(r'^statements$', views.statements, name='statements'),
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
    url(r'^stocks$', views.stocks, name='stocks'),
    # url(r'^overnight$', views.overnight_rates, name='overnight_view'),
    # url(r'^bills$', views.bill, name='bill_view'),
    # url(r'^bonds$', views.bond, name='bond_view'),
    # url(r'^libor$', views.libor, name='libor_view'),
    # url(r'^table/rates$', views.all_rates, name='all_rates'),
]
