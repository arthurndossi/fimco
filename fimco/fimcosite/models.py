from __future__ import unicode_literals

import os

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from djmoney.models.fields import MoneyField

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
PROFILE_ROOT = os.path.join(MEDIA_ROOT, 'users')

telephone = RegexValidator(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?\-?\d{2,4}){1,3}?$', 'Not a valid phone number.')


def avatar_path(instance, filename):
    current_path = '{0}/{1}/{2}'.format(PROFILE_ROOT, instance.profile_id, filename)
    if os.path.isfile(current_path):
        os.remove(current_path)
    return current_path


class Profile(models.Model):
    GENDER = (
        ('M', 'MALE'),
        ('F', 'FEMALE'),
        ('O', 'OTHER')
    )
    TYPE = (
        ('I', 'Individual'),
        ('C', 'Corporate')
    )
    STATUS = (
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PENDING', 'Pending')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField(null=True)
    gender = models.CharField(max_length=1, choices=GENDER, default='M')
    msisdn = models.CharField(validators=[telephone], max_length=14, null=True)
    pin = models.CharField(max_length=4, unique=True, null=True)
    bot_cds = models.CharField(max_length=15, null=True)
    dse_cds = models.CharField(max_length=15, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_type = models.CharField(max_length=1, choices=TYPE, default='I')
    profile_id = models.CharField(max_length=10)
    sms_notification = models.BooleanField(default=True)


class CorporateProfile(models.Model):
    FLAG = (
        ('YES', 'SET'),
        ('NO', 'UNSET')
    )
    company_name = models.CharField(max_length=100)
    address = models.TextField(max_length=500)
    account = models.CharField(max_length=15)
    admin = models.CharField(max_length=20)
    indemnity = models.CharField(max_length=1, choices=FLAG, default='NO')


class KYC(models.Model):
    profile_id = models.CharField(max_length=10, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    kyc_type = models.CharField(max_length=15)
    id_number = models.CharField(max_length=35)
    document = models.FileField(max_length=255, upload_to=avatar_path)


class Account(models.Model):
    ACTIVE_STATUS = (
        (1, 'Active'),
        (0, 'Inactive')
    )
    profile_id = models.CharField(max_length=10, db_index=True, default='NA')
    created_on = models.DateTimeField(auto_now_add=True)
    account = models.CharField(max_length=15, db_index=True)
    nickname = models.CharField(max_length=25)
    current_balance = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS')
    ts_current_bal = models.DateTimeField(null=True)
    available_balance = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS')
    ts_available_bal = models.DateTimeField(null=True)
    bonus = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS')
    ts_bonus = models.DateTimeField(null=True)
    status = models.IntegerField(choices=ACTIVE_STATUS, default=0)
    allow_overdraft = models.BooleanField(default=0)
