# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-01-13 11:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_events'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.CharField(choices=[(1, 'General'), (2, 'Authorpedia'), (3, 'College'), (4, 'Griots'), (5, 'Poetry'), (6, ('news', 'griots'))], default=1, max_length=50),
        ),
    ]