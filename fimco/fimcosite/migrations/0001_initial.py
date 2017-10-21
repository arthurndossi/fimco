# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-21 09:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('dob', models.DateField(null=True)),
                ('gender', models.CharField(choices=[('M', 'MALE'), ('F', 'FEMALE'), ('O', 'OTHER')], default='M', max_length=1)),
                ('pin', models.CharField(max_length=4, null=True, unique=True)),
                ('bot_cds', models.CharField(max_length=15, null=True)),
                ('dse_cds', models.CharField(max_length=15, null=True)),
                ('register_date', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('profile_type', models.CharField(choices=[('I', 'INDIVIDUAL'), ('C', 'CORPORATE')], max_length=1)),
                ('profile_id', models.CharField(max_length=10)),
                ('status', models.IntegerField(choices=[(0, 'ACTIVE'), (1, 'INACTIVE')], max_length=1)),
                ('approval_status', models.CharField(choices=[('APPROVED', 'APPROVED'), ('REJECTED', 'REJECTED'), ('PENDING', 'PENDING')], max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
