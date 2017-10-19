from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^$', views.home, name='pochi'),
    url(r'^dashboard$', views.admin, name='dashboard'),
    url(r'^add/account$', views.account, name='accounts'),
    url(r'^statements$', views.statements, name='statements'),
    url(r'^statement-print$', TemplateView.as_view(template_name='statement-print.html'), name='printout'),
    url(r'^pochi2pochi$', TemplateView.as_view(template_name='pochi/pochi2pochi.html'), name='pochi2pochi'),
    url(r'^withdrawal$', TemplateView.as_view(template_name='pochi/withdrawal.html'), name='withdrawal'),
    url(r'^deposit$', TemplateView.as_view(template_name='pochi/deposit.html'), name='deposit'),
    url(r'^p2p$', views.p2p, name='p2p'),
    url(r'^withdraw$', views.withdraw, name='withdraw'),
    url(r'^add$', views.add_funds, name='add'),
    url(r'^create/group$', views.new_group, name='group'),
    url(r'^view/profile$', views.view_profile, name='profile_view'),
    url(r'^group$', views.create_group, name='create_group'),
    url(r'^edit/group$', views.edit_group, name='grp_edt'),
    url(r'^edit/user$', views.edit_profile, name='usr_edt'),
    url(r'^messages$', views.notifications, name='messages'),
    url(r'^lock$', views.lock, name='lock')
]
