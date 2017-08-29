from __future__ import unicode_literals

from django.contrib import admin
from django.core.validators import RegexValidator
from django.db import models

telephone = RegexValidator(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?\-?\d{2,4}){1,3}?$', 'Not a valid phone number.')


class IndividualAccount(models.Model):
    GENDER = (
        ('M', 'MALE'),
        ('F', 'FEMALE'),
        ('T', 'TRANSGENDER')
    )
    STATUS = (
        ('PASS', 'SUCCESSFUL'),
        ('FAIL', 'UNSUCCESSFUL'),
        ('DONE', 'PENDING')
    )
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30)
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER)
    client_id = models.CharField(max_length=15, primary_key=True)
    email = models.EmailField()
    msisdn = models.CharField(max_length=12, db_index=True, default='NA', validators=[telephone])
    bot_cds = models.CharField(max_length=15, null=True)
    dse_cds = models.CharField(max_length=15, null=True)
    status = models.CharField(max_length=4, choices=STATUS)
    register_date = models.DateField(auto_created=True)
    pochi_id = models.CharField(max_length=20, null=True)


class JointAccount(models.Model):
    group_name = models.CharField(max_length=30)
    purpose = models.CharField(max_length=30, null=True)
    pochi_id = models.CharField(max_length=20, null=True)


class JointAccountAdmins(models.Model):
    group = models.ForeignKey(JointAccount, related_name='group_admins') #on_delete=models.CASCADE
    access = models.CharField(max_length=15)


class JointAccountMembers(models.Model):
    group = models.ForeignKey(JointAccount, related_name='group_members')
    members = models.CharField(max_length=15)


class JointAccountInline(admin.StackedInline):
    model = JointAccount


class GroupAdmin(admin.ModelAdmin):
    inlines = [JointAccountInline]


class MembersAdmin(admin.ModelAdmin):
    inlines = [JointAccountInline]


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
