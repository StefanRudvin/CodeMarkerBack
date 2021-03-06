# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-21 17:36
from __future__ import unicode_literals

from django.db import migrations, models
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20180217_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='languages',
            field=django_mysql.models.ListCharField(models.CharField(
                max_length=10), max_length=110, null=True, size=10),
        ),
        migrations.AddField(
            model_name='inputgenerator',
            name='language',
            field=models.CharField(default='', max_length=400),
        ),
        migrations.AddField(
            model_name='resource',
            name='language',
            field=models.CharField(default='', max_length=400),
        ),
    ]
