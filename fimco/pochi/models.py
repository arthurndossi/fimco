from __future__ import unicode_literals

from django.core.validators import RegexValidator
from django.db import models

telephone = RegexValidator(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?\-?\d{2,4}){1,3}?$', 'Not a valid phone number.')


# class JointAccount(models.Model):
#     group_name = models.CharField(max_length=30, unique=True)
#     purpose = models.CharField(max_length=30, null=True)
#     first_admin = models.CharField(max_length=30)
#     sec_admin = models.CharField(max_length=30, null=True)
#     pochi_id = models.CharField(max_length=20, null=True)
#     members = models.CharField(max_length=100, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.group_name


class Group(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    group_account = models.CharField(max_length=15, db_index=True)


class GroupMembers(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    group_account = models.CharField(max_length=15, db_index=True)
    profile_id = models.CharField(max_length=10)
    admin = models.IntegerField(default=0)


class Account(models.Model):
    ACTIVE_STATUS = (
        (0, 'ACTIVE'),
        (1, 'INACTIVE')
    )
    profile_id = models.CharField(max_length=10, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    account = models.CharField(max_length=15, db_index=True)
    currency = models.CharField(max_length=3, default='TZS')
    nickname = models.CharField(max_length=25)
    balance = models.FloatField()
    ts_balance = models.DateTimeField(null=True)
    status = models.IntegerField(choices=ACTIVE_STATUS)
    external_walletid = models.CharField(max_length=25, unique=True)


class Transaction(models.Model):
    TYPES = (
        ('DEBIT', 'DEBIT'),
        ('CREDIT', 'CREDIT')
    )

    STATUS = (
        ('SUCCESS', 'SUCCESS'),
        ('FAILED', 'FAILED'),
        ('PENDING', 'PENDING')
    )
    fulltimestamp = models.DateTimeField(auto_now_add=True)
    profile_id = models.CharField(max_length=10, db_index=True)
    account = models.CharField(max_length=15, db_index=True)
    msisdn = models.CharField(max_length=10, db_index=True, default='NA')
    external_walletid = models.CharField(max_length=25)
    trans_type = models.CharField(max_length=10, choices=TYPES)
    service = models.CharField(max_length=25, db_index=True)  # DEPOSIT, WITHDRAW, BONUS
    amount = models.CharField(max_length=25)
    charge = models.CharField(max_length=25, default='0')
    currency = models.CharField(max_length=3, default='TZS')
    reference = models.CharField(max_length=15, db_index=True, default='NA')
    status = models.CharField(max_length=4, choices=STATUS, default='DONE')
    resultcode = models.CharField(max_length=3, default='111', db_index=True)
    message = models.TextField(max_length=1024, default='NA')
    obal = models.FloatField(default=0)
    cbal = models.FloatField(default=0)
    processed_timestamp = models.DateTimeField(null=True)


class BalanceSnapshot(models.Model):
    fulltimestamp = models.DateTimeField(auto_now_add=True)
    profile_id = models.CharField(max_length=10, db_index=True)
    account = models.CharField(max_length=15, db_index=True)
    closing_balance = models.FloatField(default=0)
    bonus_closing_balance = models.FloatField(default=0)


class ExternalAccount(models.Model):
    profile_id = models.CharField(max_length=10, db_index=True)
    account_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=30)
    nickname = models.CharField(max_length=30)
    institution_name = models.CharField(max_length=100)  # Mpesa, TIGO PESA, CRDB BANK
    institution_branchcode = models.CharField(max_length=30, default='NA')
    institution_code = models.CharField(max_length=30, default='NA')
    account_type = models.CharField(max_length=3)  # MOBILE MONEY, BANK ACCOUNT


class CorporateProfile(models.Model):
    company_name = models.CharField(max_length=100)
    address = models.TextField(max_length=500)
    phone_number = models.CharField(max_length=20)
    profile_id = models.CharField(max_length=20)


class Notification(models.Model):
    profile_id = models.CharField(max_length=20)
    fulltimestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(max_length=1024, default='NA')
    read_status = models.IntegerField(default=0)
