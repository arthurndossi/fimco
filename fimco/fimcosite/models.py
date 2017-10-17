from __future__ import unicode_literals

import uuid

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

telephone = RegexValidator(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?\-?\d{2,4}){1,3}?$', 'Not a valid phone number.')


class MemberProfile(models.Model):
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
    user = models.OneToOneField(User, related_name='member', on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    dob = models.DateField(null=True)
    gender = models.CharField(max_length=1, choices=GENDER, default='M')
    client_id = models.CharField(max_length=15, unique=True, null=True)
    pin = models.CharField(max_length=4, unique=True, null=True)
    bot_cds = models.CharField(max_length=15, null=True)
    dse_cds = models.CharField(max_length=15, null=True)
    status = models.CharField(max_length=4, choices=STATUS)
    register_date = models.DateTimeField('date joined', auto_now_add=True)
    pochi_id = models.CharField(max_length=20, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            MemberProfile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.member.save()

    def clean(self):
        self.status = 'DONE'
        # self.register_date = datetime.date
        if self.get_status_display() == 'SUCCESSFUL':
            self.client_id = uuid.uuid4().hex[:6].upper()
            self.pin = uuid.uuid4().hex[:4].upper()

    def __str__(self):
        return self.pochi_id

    # post_save.connect(create_user_profile, sender=User)


class JointAccount(models.Model):
    group_name = models.CharField(max_length=30, unique=True)
    purpose = models.CharField(max_length=30, null=True)
    first_admin = models.CharField(max_length=30)
    sec_admin = models.CharField(max_length=30, null=True)
    pochi_id = models.CharField(max_length=20, null=True)
    members = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField()

    def __str__(self):
        return self.group_name


class JointAccountMembers(models.Model):
    member = models.ForeignKey('MemberProfile', on_delete=models.CASCADE)
    group = models.ForeignKey('JointAccount', related_name='group_members', on_delete=models.CASCADE)
