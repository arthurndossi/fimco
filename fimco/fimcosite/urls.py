from django.conf.urls import url

from django.contrib.auth import views as auth_views

from . import views
from .forms import FIMCOPasswordResetForm, FIMCOSetPasswordForm

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
    url(r'^login$', views.validate, name='validate'),
    url(r'^logout$', views.log_out, name='logout'),
    url(r'^account/password/reset/$', auth_views.password_reset,
        {
            'email_template_name': 'password-reset-email.html',
            'template_name': 'forgot.html',
            'subject_template_name': 'password-reset-subject.txt',
            'from_email': 'admin@fimco.co.tz',
            'password_reset_form': FIMCOPasswordResetForm
        }, name='password_reset'),
    url(r'^account/password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {
            'template_name': 'password-reset.html',
            'set_password_form': FIMCOSetPasswordForm
        }, name='password_reset_confirm'),
    url(r'^account/password/done/$', auth_views.password_reset_done, {'template_name': "password-reset-done.html"},
        name='password_reset_done'),
    url(r'^reset/complete/$', auth_views.password_reset_complete,
        {'template_name': 'password-reset-complete.html'}, name='password_reset_complete'),
]
