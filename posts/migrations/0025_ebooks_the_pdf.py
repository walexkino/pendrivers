# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-06-01 00:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0024_auto_20180529_0918'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebooks',
            name='the_pdf',
            field=models.CharField(default='None', max_length=250),
        ),
    ]
