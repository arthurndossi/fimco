from __future__ import unicode_literals

import os
import uuid

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
PROFILE_ROOT = os.path.join(MEDIA_ROOT, 'kyc', 'documents')

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
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    profile_type = models.CharField(max_length=1, choices=TYPE, default='I')
    profile_id = models.CharField(max_length=10)
    status = models.IntegerField(choices=ACTIVE_STATUS, default=0)
    approval_status = models.CharField(max_length=10, choices=STATUS, default='PENDING')

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __init__(self, *args, **kwargs):
        super(Profile, self).__init__(*args, **kwargs)
        self.profile_id = "POC%s" % uuid.uuid4().hex[:6].upper()
        self.pin = uuid.uuid4().hex[:4].upper()


class CorporateProfile(models.Model):
    company_name = models.CharField(max_length=100)
    address = models.TextField(max_length=500)
    phone_number = models.CharField(max_length=20)
    profile_id = models.CharField(max_length=20)
    website = models.URLField(max_length=100, default='NA')


class KYC(models.Model):
    profile_id = models.CharField(max_length=10, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    kyc_type = models.CharField(max_length=15)
    id_number = models.CharField(max_length=35)
    document = models.FileField(max_length=255, upload_to=avatar_path)
