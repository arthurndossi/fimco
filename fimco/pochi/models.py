from __future__ import unicode_literals

import uuid

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models

# from fimco.fimcosite.models import Profile
from django.utils import timezone

telephone = RegexValidator(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?\-?\d{2,4}){1,3}?$', 'Not a valid phone number.')


class Stocks(models.Model):
    name = models.CharField(max_length=30)
    price = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=4, decimal_places=2)


class Bonds(models.Model):
    name = models.CharField(max_length=30)
    bond_yield = models.DecimalField(max_digits=6, decimal_places=3)
    change = models.DecimalField(max_digits=6, decimal_places=3)


class Currencies(models.Model):
    home = models.CharField(max_length=3)
    away = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=6, decimal_places=4)


class Commodities(models.Model):
    index = models.CharField(max_length=15)
    last = models.DecimalField(max_digits=6, decimal_places=2)
    change = models.DecimalField(max_digits=4, decimal_places=2)


class Exchange(models.Model):
    exchange = models.ForeignKey(Currencies, related_name='exchange')
    date = models.DateTimeField(auto_now=True)
    day_high = models.DecimalField(max_digits=7, decimal_places=4)
    day_low = models.DecimalField(max_digits=7, decimal_places=4)
    # last
    percentage_change = models.DecimalField(max_digits=4, decimal_places=2)
    bid = models.DecimalField(max_digits=7, decimal_places=4)
    offer = models.DecimalField(max_digits=6, decimal_places=4)


class JointAccount(models.Model):
    group_name = models.CharField(max_length=30, unique=True)
    purpose = models.CharField(max_length=30, null=True)
    first_admin = models.CharField(max_length=30)
    sec_admin = models.CharField(max_length=30, null=True)
    pochi_id = models.CharField(max_length=20, null=True)
    members = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.group_name

    def save(self, *args, **kwargs):
        if not self.pochi_id:
            # This code only happens if the objects is
            # not in the database yet. Otherwise it would
            # have pk
            self.pochi_id = uuid.uuid4().hex[:6].upper()
        super(JointAccount, self).save(args, kwargs)


class Transactions(models.Model):
    TYPES = (
        ('W', 'WITHDRAW'),
        ('D', 'DEPOSIT'),
        ('P', 'POCHI')
    )
    STATUS = (
        ('PASS', 'SUCCESSFUL'),
        ('FAIL', 'UNSUCCESSFUL'),
        ('DONE', 'PENDING')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    msisdn = models.CharField(max_length=10, db_index=True, default='NA')
    trans_timestamp = models.DateTimeField(default=timezone.now)
    processed_timestamp = models.DateTimeField(null=True)
    amount = models.CharField(max_length=25)
    currency = models.CharField(max_length=3, default='TZS')
    type = models.CharField(max_length=1, choices=TYPES)
    status = models.CharField(max_length=4, choices=STATUS, default='DONE')
    result_code = models.CharField(max_length=3, default='111', db_index=True)
    open_bal = models.IntegerField(default=0)
    close_bal = models.IntegerField(default=0)
    message = models.TextField(max_length=1024, default='NA')
    reference = models.CharField(max_length=15, db_index=True, default='NA')
