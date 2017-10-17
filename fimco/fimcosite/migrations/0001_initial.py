# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-17 11:46
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
            name='JointAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=30, unique=True)),
                ('purpose', models.CharField(max_length=30, null=True)),
                ('first_admin', models.CharField(max_length=30)),
                ('sec_admin', models.CharField(max_length=30, null=True)),
                ('pochi_id', models.CharField(max_length=20, null=True)),
                ('created_at', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='JointAccountMembers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_members', to='fimcosite.JointAccount')),
            ],
        ),
        migrations.CreateModel(
            name='MemberProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('dob', models.DateField(null=True)),
                ('gender', models.CharField(choices=[('M', 'MALE'), ('F', 'FEMALE'), ('O', 'OTHER')], default='M', max_length=1)),
                ('client_id', models.CharField(max_length=15, null=True, unique=True)),
                ('pin', models.CharField(max_length=4, null=True, unique=True)),
                ('bot_cds', models.CharField(max_length=15, null=True)),
                ('dse_cds', models.CharField(max_length=15, null=True)),
                ('status', models.CharField(choices=[('PASS', 'SUCCESSFUL'), ('FAIL', 'UNSUCCESSFUL'), ('DONE', 'PENDING')], max_length=4)),
                ('register_date', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('pochi_id', models.CharField(max_length=20, null=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='jointaccountmembers',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fimcosite.MemberProfile'),
        ),
        migrations.AddField(
            model_name='jointaccount',
            name='members',
            field=models.ManyToManyField(through='fimcosite.JointAccountMembers', to='fimcosite.MemberProfile'),
        ),
    ]
