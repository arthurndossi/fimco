from __future__ import unicode_literals

from django.core.validators import RegexValidator
from django.db import models

telephone = RegexValidator(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?\-?\d{2,4}){1,3}?$', 'Not a valid phone number.')


class Group(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=30, unique=True)
    group_account = models.CharField(max_length=15, db_index=True)
    balance = models.FloatField(default=0)


class GroupMember(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    group_account = models.CharField(max_length=15, db_index=True)
    profile_id = models.CharField(max_length=10)
    admin = models.IntegerField(default=0)


class Transaction(models.Model):
    STATUS = (
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending')
    )
    SERVICES = (
        ('P2P', 'p2p'),
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
        ('INTEREST', 'Interest'),
    )
    MODES = (
        ('POCHI', 'Pochi'),
        ('MOBILE', 'Mobile'),
        ('BANK', 'Bank'),
        ('CASH', 'Cash'),
    )
    full_timestamp = models.DateTimeField(auto_now_add=True)
    profile_id = models.CharField(max_length=10, db_index=True)
    account = models.CharField(max_length=15, db_index=True)
    msisdn = models.CharField(max_length=10, db_index=True, default='NA')
    external_wallet_id = models.CharField(max_length=25, default='NA')
    service = models.CharField(max_length=8, db_index=True, choices=SERVICES)
    channel = models.CharField(max_length=25, db_index=True, default='NA')
    mode = models.CharField(max_length=6, db_index=True, choices=MODES, default='POCHI')
    dest_account = models.CharField(max_length=25, db_index=True, default='NA')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    charge = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='TZS')
    reference = models.CharField(max_length=15, db_index=True, default='NA')
    status = models.CharField(max_length=7, choices=STATUS, default='PENDING')
    result_code = models.CharField(max_length=3, default='111', db_index=True)
    message = models.TextField(max_length=1024, default='NA')
    processed_timestamp = models.DateTimeField(null=True)


class Ledger(models.Model):
    TYPES = (
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit')
    )
    full_timestamp = models.DateTimeField(auto_now_add=True)
    profile_id = models.CharField(max_length=10, db_index=True, default='POC0GL0001')
    account = models.CharField(max_length=15, db_index=True, default='GL0001')
    trans_type = models.CharField(max_length=10, choices=TYPES)
    service = models.CharField(max_length=25, db_index=True)  # DEPOSIT, WITHDRAW, BONUS, P2P
    channel = models.CharField(max_length=25, db_index=True, default='NA') #system
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='TZS')
    reference = models.CharField(max_length=15, db_index=True, default='NA')
    o_bal = models.FloatField(default=0)
    c_bal = models.FloatField(default=0)


class BalanceSnapshot(models.Model):
    full_timestamp = models.DateTimeField(auto_now_add=True)
    profile_id = models.CharField(max_length=10, db_index=True)
    account = models.CharField(max_length=15, db_index=True)
    closing_balance = models.FloatField(default=0)
    bonus_closing_balance = models.FloatField(default=0)


class ExternalAccount(models.Model):
    ACCOUNTS = (
        ('MM', 'MOBILE MONEY'),
        ('BA', 'BANK ACCOUNT')
    )
    profile_id = models.CharField(max_length=10, db_index=True)
    account_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=30, default='NA')
    institution_name = models.CharField(max_length=100)  # Mpesa, TIGO PESA, CRDB BANK
    institution_branchcode = models.CharField(max_length=30, default='NA')
    institution_code = models.CharField(max_length=30, default='NA')
    account_type = models.CharField(max_length=2, choices=ACCOUNTS)


class Notification(models.Model):
    profile_id = models.CharField(max_length=20)
    full_timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(max_length=1024, default='NA')
    read_status = models.IntegerField(default=0)


class PaidUser(models.Model):
    TYPES = (
        ('STANDARD', 'Free'),
        ('PREMIUM', 'Premium')
    )
    profile_id = models.CharField(max_length=20)
    level = models.CharField(max_length=10, choices=TYPES)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True)


class Charge(models.Model):
    service = models.CharField(max_length=8)
    charge = models.FloatField(default=0)


class Rate(models.Model):
    full_timestamp = models.DateField(auto_now_add=True)
    rate = models.FloatField(default=0)


class CashOut(models.Model):
    STATUS = (
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending')
    )
    ext_entity = models.CharField(max_length=100)
    ext_acc_no = models.CharField(max_length=30, default='NA')
    amount = models.FloatField(default=0)
    status = models.CharField(max_length=8, choices=STATUS, default='PENDING')
