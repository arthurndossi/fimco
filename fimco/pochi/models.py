from __future__ import unicode_literals

from django.core.validators import RegexValidator
from django.db import models
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator, MaxMoneyValidator

telephone = RegexValidator(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?\-?\d{2,4}){1,3}?$', 'Not a valid phone number.')


class Group(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=30, unique=True)
    account = models.CharField(max_length=15, db_index=True)


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
    trans_id = models.CharField(max_length=25, default='NA')
    service = models.CharField(max_length=8, db_index=True, choices=SERVICES)
    channel = models.CharField(max_length=25, db_index=True, default='NA')
    mode = models.CharField(max_length=6, db_index=True, choices=MODES, default='POCHI')
    dst_account = models.CharField(max_length=25, db_index=True, default='NA')
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS',
                        validators=[
                            MinMoneyValidator({'TZS': 1000, 'USD': 50}),
                            MaxMoneyValidator({'TZS': 1000000000, 'USD': 1000000}),
                        ])
    charge = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS')
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
    channel = models.CharField(max_length=25, db_index=True, default='NA')  # system
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS',
                        validators=[
                            MinMoneyValidator({'TZS': 1000, 'USD': 50}),
                            MaxMoneyValidator({'TZS': 1000000000, 'USD': 1000000}),
                        ])
    reference = models.CharField(max_length=15, db_index=True, default='NA')
    available_o_bal = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS')
    available_c_bal = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS')
    current_o_bal = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS')
    current_c_bal = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS')


class BalanceSnapshot(models.Model):
    full_timestamp = models.DateTimeField(auto_now_add=True)
    profile_id = models.CharField(max_length=10, db_index=True)
    account = models.CharField(max_length=15, db_index=True)
    available_closing_balance = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS')
    current_closing_balance = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS')
    bonus_closing_balance = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS')


class ExternalAccount(models.Model):
    ACCOUNTS = (
        ('MM', 'MOBILE MONEY'),
        ('BA', 'BANK ACCOUNT')
    )
    profile_id = models.CharField(max_length=10, db_index=True)
    account_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=30, default='NA')
    institution_name = models.CharField(max_length=100)  # M-PESA, TIGO-PESA, CRDB-BANK
    institution_branch = models.CharField(max_length=30, default='NA')
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
    charge = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS')


class Rate(models.Model):
    full_timestamp = models.DateField(auto_now_add=True)
    rate = models.FloatField(default=0)


class SMSCount(models.Model):
    profile_id = models.CharField(max_length=20)
    count = models.IntegerField(default=0)


class CashOut(models.Model):
    STATUS = (
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending')
    )
    ext_entity = models.CharField(max_length=100)
    ext_acc_no = models.CharField(max_length=30, default='NA')
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='TZS',
                        validators=[
                            MinMoneyValidator({'TZS': 1000, 'USD': 50}),
                            MaxMoneyValidator({'TZS': 1000000000, 'USD': 1000000}),
                        ])
    status = models.CharField(max_length=8, choices=STATUS, default='PENDING')
    result = models.CharField(max_length=3, default='111', db_index=True)
    message = models.TextField(max_length=1024, default='NA')
    reference = models.CharField(max_length=15, db_index=True, default='NA')
    ext_trans_id = models.CharField(max_length=25, default='NA')
