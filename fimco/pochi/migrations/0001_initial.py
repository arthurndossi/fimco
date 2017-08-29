# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-07-27 12:10
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
            name='IndividualAccount',
            fields=[
                ('register_date', models.DateField(auto_created=True)),
                ('first_name', models.CharField(max_length=30)),
                ('middle_name', models.CharField(max_length=30, null=True)),
                ('last_name', models.CharField(max_length=30)),
                ('dob', models.DateField()),
                ('gender', models.CharField(choices=[('M', 'MALE'), ('F', 'FEMALE'), ('T', 'TRANSGENDER')], max_length=1)),
                ('client_id', models.CharField(max_length=15, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254)),
                ('msisdn', models.CharField(db_index=True, default='NA', max_length=12, validators=[django.core.validators.RegexValidator('^([+]?(\\d{1,3}\\s?)|[0])\\s?\\d+(\\s?\\-?\\d{2,4}){1,3}?$', 'Not a valid phone number.')])),
                ('bot_cds', models.CharField(max_length=15, null=True)),
                ('dse_cds', models.CharField(max_length=15, null=True)),
                ('status', models.CharField(choices=[('PASS', 'SUCCESSFUL'), ('FAIL', 'UNSUCCESSFUL'), ('DONE', 'PENDING')], max_length=4)),
                ('pochi_id', models.CharField(max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='JointAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=30)),
                ('purpose', models.CharField(max_length=30, null=True)),
                ('pochi_id', models.CharField(max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='JointAccountAdmins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access', models.CharField(max_length=15)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_admins', to='pochi.JointAccount')),
            ],
        ),
        migrations.CreateModel(
            name='JointAccountMembers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('members', models.CharField(max_length=15)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_members', to='pochi.JointAccount')),
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
    ]
