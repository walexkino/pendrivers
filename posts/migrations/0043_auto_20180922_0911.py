# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-09-22 09:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0042_auto_20180921_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.CharField(choices=[('Adventure', 'Adventure'), ('Horror', 'Horror'), ('Romance', 'Romance'), ('Epic', 'Epic'), ('Thriller', 'Thriller'), ('Humour', 'Humour'), ('Legend', 'Legend'), ('Satire', 'Satire'), ('Sci-Fi', 'Sci-Fi'), ('Urban', 'Urban'), ('History', 'History'), ('Fan Fiction', 'Fan Fiction'), ('Others', 'Others'), ('Humor', 'Humor'), ('Tragedy', 'Tragedy'), ('Romance', 'Romance'), ('Ode', 'Ode'), ('Epic', 'Epic'), ('Nolstagia', 'Nolstagia'), ('Nature', 'Nature'), ('Didactics', 'Didactics'), ('Peace', 'Peace'), ('Satire', 'Satire'), ('Sexuality', 'Sexuality'), ('Business', 'Business'), ('Education', 'Education'), ('Family', 'Family'), ('Children', 'Children'), ('Finance', 'Finance'), ('Food', 'Food'), ('Spirituality', 'Spirituality'), ('Technology', 'Technology'), ('Politics', 'Politics'), ('Religion', 'Religion'), ('Art', 'Art'), ('Music', 'Music'), ('Photography', 'Photography')], default='Others', max_length=120),
        ),
    ]
