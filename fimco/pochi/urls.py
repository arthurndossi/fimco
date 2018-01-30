from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='pochi'),
    url(r'^dashboard$', views.admin, name='dashboard'),
    url(r'^dashboard/(?P<page>[a-zA-Z]+)$', views.view_data, name='data'),
    url(r'^add/account$', views.account, name='accounts'),
    url(r'^statements$', views.statement, name='statements'),
    url(r'^pochi2pochi', views.pochi2pochi, name='pochi2pochi'),
    url(r'^withdraw$', views.withdraw, name='withdraw'),
    url(r'^confirm/remove/bank$', views.confirm_delete_bank_acc, name='confirm_del_bank'),
    url(r'^remove/bank$', views.del_bank_acc, name='del_bank'),
    url(r'^how/to/deposit$', views.how_to_deposit, name='deposit'),
    url(r'^deposit$', views.deposit),
    url(r'^mobile/withdraw$', views.mobile, name='mobile'),
    url(r'^create/group$', views.new_group, name='group'),
    url(r'^view/profile$', views.view_profile, name='profile_view'),
    url(r'^group$', views.create_group, name='create_group'),
    url(r'^(?P<name>[ a-zA-Z\-]+)/dashboard$', views.admin, name='group_dashboard'),
    url(r'^(?P<name>[ a-zA-Z\-]+)/dashboard/(?P<page>[a-zA-Z]+)$', views.view_data, name='group_data'),
    url(r'^(?P<name>[ a-zA-Z\-]+)/balance$', views.group_profile, name='group_balance'),
    url(r'^(?P<name>[ a-zA-Z\-]+)/statement$', views.group_statement, name='group_statement'),
    url(r'^(?P<name>[ a-zA-Z\-]+)/(?P<action>[a-z]+)/member$', views.add_remove_member, name='group_member'),
    url(r'^(?P<name>[ a-zA-Z\-]+)/settings$', views.group_settings, name='group_settings'),
    url(r'^(?P<name>[ a-zA-Z\-]+)/activity$', views.pochi2pochi, name='group_activity'),
    url(r'^(?P<name>[ a-zA-Z\-]+)/exit$', views.exit_group, name='exit_group'),
    url(r'^(?P<name>[ a-zA-Z\-]+)/confirm/(?P<action>[0-9a-zA-Z\-]+)$', views.confirm_action_group,
        name='confirm_action_group'),
    url(r'^(?P<name>[ a-zA-Z\-]+)/(?P<identity>[0-9a-zA-Z\-]+)/(?P<action>[a-z]+)$', views.group_admin,
        name='group_admin'),
    url(r'^(?P<name>[ a-zA-Z\-]+)/delete$', views.delete_group, name='del_group'),
    url(r'^edit/group$', views.edit_group, name='grp_edt'),
    url(r'^edit/user$', views.edit_profile, name='usr_edt'),
    url(r'^lock$', views.lock, name='lock'),
    url(r'^delete/account$', views.delete_account, name='delete_account'),
    url(r'^confirm/transfer$', views.confirm_transfer, name='confirm'),
    url(r'^check/user$', views.validate_pochi_id, name='check'),
    url(r'^(?P<type>[a-zA-Z]+)/form$', views.IndemnityPDF.as_view(), name='create_form'),
]
