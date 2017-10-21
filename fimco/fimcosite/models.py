from __future__ import unicode_literals

import uuid

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

telephone = RegexValidator(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?\-?\d{2,4}){1,3}?$', 'Not a valid phone number.')


class Profile(models.Model):
    GENDER = (
        ('M', 'MALE'),
        ('F', 'FEMALE'),
        ('O', 'OTHER')
    )

    TYPE = (
        ('I', 'INDIVIDUAL'),
        ('C', 'CORPORATE')
    )
    STATUS = (
        ('APPROVED', 'APPROVED'),
        ('REJECTED', 'REJECTED'),
        ('PENDING', 'PENDING')
    )

    ACTIVE_STATUS = (
        (0, 'ACTIVE'),
        (1, 'INACTIVE')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField(null=True)
    gender = models.CharField(max_length=1, choices=GENDER, default='M')
    pin = models.CharField(max_length=4, unique=True, null=True)
    bot_cds = models.CharField(max_length=15, null=True)
    dse_cds = models.CharField(max_length=15, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    profile_type = models.CharField(max_length=1, choices=TYPE)
    profile_id = models.CharField(max_length=10)
    status = models.IntegerField(max_length=1, choices=ACTIVE_STATUS)
    approval_status = models.CharField(max_length=10, choices=STATUS)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def clean(self):
        self.profile_id = uuid.uuid4().hex[:6].upper()
        self.pin = uuid.uuid4().hex[:4].upper()

    post_save.connect(create_user_profile, sender=User)


class KYC(models.Model):
    profile_id = models.CharField(max_length=10, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    kyc_type = models.CharField(max_length=15)
    id_type = models.CharField(max_length=15)
    id_number = models.CharField(max_length=35)
    document = models.FileField(upload_to='documents/')
