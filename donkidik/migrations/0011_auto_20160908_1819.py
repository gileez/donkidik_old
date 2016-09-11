# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-08 18:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('donkidik', '0010_post_modified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='votes',
        ),
        migrations.AddField(
            model_name='post',
            name='downvotes',
            field=models.ManyToManyField(related_name='downvoted_posts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='post',
            name='upvotes',
            field=models.ManyToManyField(related_name='upvoted_posts', to=settings.AUTH_USER_MODEL),
        ),
    ]