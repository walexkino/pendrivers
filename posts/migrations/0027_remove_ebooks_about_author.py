# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-06-01 00:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0026_remove_ebooks_book_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ebooks',
            name='about_author',
        ),
    ]