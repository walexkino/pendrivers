# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-01-13 12:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20180113_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.CharField(choices=[('1', 'Guest Post'), ('2', 'Griots'), ('3', 'Class'), ('4', 'Dictionary'), ('5', 'Biography'), ('6', 'Articles'), ('7', 'Bookshop')], default='1', max_length=50),
        ),
    ]
