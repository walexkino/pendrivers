# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-08-30 10:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0003_contestant_bought_book'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contestant',
            name='manuscript',
            field=models.FileField(null=True, upload_to='manuscripts'),
        ),
    ]
