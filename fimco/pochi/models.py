from __future__ import unicode_literals

from django.core.validators import RegexValidator
from django.db import models

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
