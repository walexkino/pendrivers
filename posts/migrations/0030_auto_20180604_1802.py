# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-06-04 18:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0029_post_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.CharField(default='others', max_length=120),
        ),
    ]
