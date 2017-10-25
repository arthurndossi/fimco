from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^$', views.home, name='pochi'),
    url(r'^dashboard$', views.admin, name='dashboard'),
    url(r'^add/account$', views.account, name='accounts'),
    url(r'^statements$', views.statements, name='statements'),
    url(r'^statement-print$', TemplateView.as_view(template_name='statement-print.html'), name='printout'),
    url(r'^pochi2pochi', views.pochi2pochi, name='pochi2pochi'),
    url(r'^withdrawal$', views.withdraw, name='withdrawal'),
    url(r'^deposit$', TemplateView.as_view(template_name='pochi/deposit.html'), name='deposit'),
    url(r'^p2p/process$', views.process_p2p, name='process_p2p'),
    url(r'^withdraw$', views.withdraw, name='withdraw'),
    url(r'^add$', views.withdraw, name='add'),
    url(r'^create/group$', views.new_group, name='group'),
    url(r'^view/profile$', views.view_profile, name='profile_view'),
    url(r'^group$', views.create_group, name='create_group'),
    url(r'^(?P<name>[a-zA-Z])/dashboard$', views.group_profile, name='group_profile'),
    url(r'^(?P<name>[a-zA-Z])/statement$', views.group_statement, name='group_statement'),
    url(r'^(?P<name>[a-zA-Z])/add/member$', views.add_member, name='add_member'),
    url(r'^group/settings$', views.group_settings, name='group_settings'),
    url(r'^edit/group$', views.edit_group, name='grp_edt'),
    url(r'^edit/user$', views.edit_profile, name='usr_edt'),
    url(r'^lock$', views.lock, name='lock')
]
