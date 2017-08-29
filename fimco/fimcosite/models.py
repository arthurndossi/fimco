from __future__ import unicode_literals

from datetime import datetime
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

telephone = RegexValidator(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?\-?\d{2,4}){1,3}?$', 'Not a valid phone number.')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField
    gender = models.CharField
    identity_type = models.CharField
    identity = models.CharField
    scanned_id = models.ImageField
    phone = models.CharField
    image = models.ImageField

    bot_account = models.CharField
    dse_account = models.CharField

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


def generate_client_id():
    pass


def generate_pin():
    pass


class IndividualAccount(models.Model):
    GENDER = (
        ('M', 'MALE'),
        ('F', 'FEMALE'),
        ('O', 'OTHER')
    )
    STATUS = (
        ('PASS', 'SUCCESSFUL'),
        ('FAIL', 'UNSUCCESSFUL'),
        ('DONE', 'PENDING')
    )
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER)
    client_id = models.CharField(max_length=15, unique=True, primary_key=True)
    pin = models.CharField(max_length=4, unique=True, null=True)
    email = models.EmailField()
    msisdn = models.CharField(max_length=12, db_index=True, default='NA', validators=[telephone])
    bot_cds = models.CharField(max_length=15, null=True)
    dse_cds = models.CharField(max_length=15, null=True)
    status = models.CharField(max_length=4, choices=STATUS)
    register_date = models.DateField(auto_created=True)
    pochi_id = models.CharField(max_length=20, null=True)

    def clean(self):
        self.status = 'DONE'
        self.register_date = datetime.date
        if self.get_status_display() == 'SUCCESSFUL':
            self.client_id = generate_client_id()
            self.pin = generate_pin()

    def __str__(self):
        return self.pochi_id


class JointAccount(models.Model):
    # Group ID
    group_name = models.CharField(max_length=30, unique=True)
    purpose = models.CharField(max_length=30, null=True)
    first_admin = models.CharField(max_length=30)
    sec_admin = models.CharField(max_length=30, null=True)
    pochi_id = models.CharField(max_length=20, null=True)
    members = models.ManyToManyField(IndividualAccount, through='JointAccountMembers')
    members_count = models.IntegerField()
    created_at = models.DateTimeField()

    def __str__(self):
        return self.group_name


class JointAccountMembers(models.Model):
    member = models.ForeignKey(IndividualAccount, on_delete=models.CASCADE)
    group = models.ForeignKey(JointAccount, related_name='group_members', on_delete=models.CASCADE)


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
