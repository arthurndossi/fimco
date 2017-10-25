from __future__ import unicode_literals

from django.core.validators import RegexValidator
from django.db import models

telephone = RegexValidator(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?\-?\d{2,4}){1,3}?$', 'Not a valid phone number.')


class Group(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    group_account = models.CharField(max_length=15, db_index=True)


class GroupMembers(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    group_account = models.CharField(max_length=15, db_index=True)
    profile_id = models.CharField(max_length=10)
    admin = models.IntegerField(default=0)


class Transaction(models.Model):
    STATUS = (
        ('SUCCESS', 'SUCCESS'),
        ('FAILED', 'FAILED'),
        ('PENDING', 'PENDING')
    )
    fulltimestamp = models.DateTimeField(auto_now_add=True)
    profile_id = models.CharField(max_length=10, db_index=True)
    account = models.CharField(max_length=15, db_index=True)
    msisdn = models.CharField(max_length=10, db_index=True, default='NA')
    external_walletid = models.CharField(max_length=25, default='NA')
    service = models.CharField(max_length=25, db_index=True)  # DEPOSIT, WITHDRAW, BONUS, P2P
    channel = models.CharField(max_length=25, db_index=True, default='NA')
    dest_account = models.CharField(max_length=25, db_index=True, default='NA')
    amount = models.CharField(max_length=25)
    charge = models.CharField(max_length=25, default='0')
    currency = models.CharField(max_length=3, default='TZS')
    reference = models.CharField(max_length=15, db_index=True, default='NA')
    status = models.CharField(max_length=4, choices=STATUS, default='DONE')
    resultcode = models.CharField(max_length=3, default='111', db_index=True)
    message = models.TextField(max_length=1024, default='NA')
    processed_timestamp = models.DateTimeField(null=True)


class Ledger(models.Model):
    TYPES = (
        ('DEBIT', 'DEBIT'),
        ('CREDIT', 'CREDIT')
    )
    fulltimestamp = models.DateTimeField(auto_now_add=True)
    profile_id = models.CharField(max_length=10, db_index=True)
    account = models.CharField(max_length=15, db_index=True)
    trans_type = models.CharField(max_length=10, choices=TYPES)
    service = models.CharField(max_length=25, db_index=True)  # DEPOSIT, WITHDRAW, BONUS, P2P
    channel = models.CharField(max_length=25, db_index=True, default='NA')
    amount = models.CharField(max_length=25)
    currency = models.CharField(max_length=3, default='TZS')
    reference = models.CharField(max_length=15, db_index=True, default='NA')
    obal = models.FloatField(default=0)
    cbal = models.FloatField(default=0)


class BalanceSnapshot(models.Model):
    fulltimestamp = models.DateTimeField(auto_now_add=True)
    profile_id = models.CharField(max_length=10, db_index=True)
    account = models.CharField(max_length=15, db_index=True)
    closing_balance = models.FloatField(default=0)
    bonus_closing_balance = models.FloatField(default=0)


class ExternalAccount(models.Model):
    profile_id = models.CharField(max_length=10, db_index=True)
    account_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=30, default='NA')
    nickname = models.CharField(max_length=30, default='NA')
    institution_name = models.CharField(max_length=100)  # Mpesa, TIGO PESA, CRDB BANK
    institution_branchcode = models.CharField(max_length=30, default='NA')
    institution_code = models.CharField(max_length=30, default='NA')
    account_type = models.CharField(max_length=3)  # MOBILE MONEY, BANK ACCOUNT


class Notification(models.Model):
    profile_id = models.CharField(max_length=20)
    fulltimestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(max_length=1024, default='NA')
    read_status = models.IntegerField(default=0)
