# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-17 23:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bonds',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('bond_yield', models.DecimalField(decimal_places=3, max_digits=6)),
                ('change', models.DecimalField(decimal_places=3, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='Commodities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.CharField(max_length=15)),
                ('last', models.DecimalField(decimal_places=2, max_digits=6)),
                ('change', models.DecimalField(decimal_places=2, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='Currencies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('home', models.CharField(max_length=3)),
                ('away', models.CharField(max_length=3)),
                ('rate', models.DecimalField(decimal_places=4, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='Exchange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True)),
                ('day_high', models.DecimalField(decimal_places=4, max_digits=7)),
                ('day_low', models.DecimalField(decimal_places=4, max_digits=7)),
                ('percentage_change', models.DecimalField(decimal_places=2, max_digits=4)),
                ('bid', models.DecimalField(decimal_places=4, max_digits=7)),
                ('offer', models.DecimalField(decimal_places=4, max_digits=6)),
                ('exchange', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchange', to='pochi.Currencies')),
            ],
        ),
        migrations.CreateModel(
            name='JointAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=30, unique=True)),
                ('purpose', models.CharField(max_length=30, null=True)),
                ('first_admin', models.CharField(max_length=30)),
                ('sec_admin', models.CharField(max_length=30, null=True)),
                ('pochi_id', models.CharField(max_length=20, null=True)),
                ('members', models.CharField(max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Stocks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('price', models.PositiveIntegerField()),
                ('rate', models.DecimalField(decimal_places=2, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('msisdn', models.CharField(db_index=True, default='NA', max_length=10)),
                ('trans_timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('processed_timestamp', models.DateTimeField(null=True)),
                ('amount', models.CharField(max_length=25)),
                ('currency', models.CharField(default='TZS', max_length=3)),
                ('type', models.CharField(choices=[('W', 'WITHDRAW'), ('D', 'DEPOSIT'), ('P', 'POCHI')], max_length=1)),
                ('status', models.CharField(choices=[('PASS', 'SUCCESSFUL'), ('FAIL', 'UNSUCCESSFUL'), ('DONE', 'PENDING')], default='DONE', max_length=4)),
                ('result_code', models.CharField(db_index=True, default='111', max_length=3)),
                ('open_bal', models.IntegerField(default=0)),
                ('close_bal', models.IntegerField(default=0)),
                ('message', models.TextField(default='NA', max_length=1024)),
                ('reference', models.CharField(db_index=True, default='NA', max_length=15)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
