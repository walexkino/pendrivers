# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-01-05 23:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20180104_2157'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='category',
            field=models.CharField(choices=[(1, 'General'), (2, 'Authorpedia'), (3, 'College'), (4, 'Griots'), (5, 'Poetry'), (6, 'News')], default=1, max_length=50),
        ),
    ]
