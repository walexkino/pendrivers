# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-09-16 23:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0039_auto_20180912_0755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.CharField(choices=[('Adventure', 'Adventure'), ('Horror', 'Horror'), ('Romance', 'Romance'), ('Epic', 'Epic'), ('Thriller', 'Thriller'), ('Humour', 'Humour'), ('Legend', 'Legend'), ('Satire', 'Satire'), ('Sci-Fi', 'Sci-Fi'), ('Urban', 'Urban'), ('History', 'History'), ('Others', 'Others')], default='Others', max_length=120),
        ),
    ]
