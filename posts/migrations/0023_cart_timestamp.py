# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-05-29 07:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0022_cart'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]