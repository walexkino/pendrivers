# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-06-04 17:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0028_bought'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.CharField(default='article', max_length=120),
        ),
    ]
