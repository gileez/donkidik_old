# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-26 16:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donkidik', '0011_auto_20160908_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='post_type',
            field=models.IntegerField(choices=[(1, b'General'), (2, b'Report')], db_index=True, default=1),
        ),
    ]
