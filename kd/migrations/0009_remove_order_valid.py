# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-04 23:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kd', '0008_auto_20160704_0516'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='valid',
        ),
    ]