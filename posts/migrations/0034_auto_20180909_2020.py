# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-09-09 20:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0033_auto_20180830_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='college',
            name='height_field',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='college',
            name='width_field',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='height_field',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='width_field',
            field=models.IntegerField(default=0, null=True),
        ),
    ]