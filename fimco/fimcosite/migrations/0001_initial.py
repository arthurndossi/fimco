# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-11-02 14:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import fimcosite.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_id', models.CharField(db_index=True, max_length=10)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('account', models.CharField(db_index=True, max_length=15)),
                ('currency', models.CharField(default='TZS', max_length=3)),
                ('nickname', models.CharField(max_length=25)),
                ('balance', models.FloatField(default=0)),
                ('ts_balance', models.DateTimeField(null=True)),
                ('status', models.IntegerField(choices=[(0, 'ACTIVE'), (1, 'INACTIVE')], default=0)),
                ('external_walletid', models.CharField(default='NA', max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='CorporateProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=100)),
                ('address', models.TextField(max_length=500)),
                ('phone_number', models.CharField(max_length=20)),
                ('profile_id', models.CharField(max_length=20)),
                ('website', models.URLField(default='NA', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='KYC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_id', models.CharField(db_index=True, max_length=10)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('kyc_type', models.CharField(max_length=15)),
                ('id_number', models.CharField(max_length=35)),
                ('document', models.FileField(max_length=255, upload_to=fimcosite.models.avatar_path)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dob', models.DateField(null=True)),
                ('gender', models.CharField(choices=[('M', 'MALE'), ('F', 'FEMALE'), ('O', 'OTHER')], default='M', max_length=1)),
                ('pin', models.CharField(max_length=4, null=True, unique=True)),
                ('bot_cds', models.CharField(max_length=15, null=True)),
                ('dse_cds', models.CharField(max_length=15, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('profile_type', models.CharField(choices=[('I', 'INDIVIDUAL'), ('C', 'CORPORATE')], default='I', max_length=1)),
                ('profile_id', models.CharField(max_length=10)),
                ('status', models.IntegerField(choices=[(0, 'ACTIVE'), (1, 'INACTIVE')], default=0)),
                ('approval_status', models.CharField(choices=[('APPROVED', 'APPROVED'), ('REJECTED', 'REJECTED'), ('PENDING', 'PENDING')], default='PENDING', max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]