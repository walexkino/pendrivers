# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-07-16 15:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20180502_0428'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='website',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='social_media',
            field=models.CharField(default='', max_length=120),
        ),
    ]