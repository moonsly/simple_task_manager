# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-02-07 22:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('status', models.PositiveIntegerField(choices=[(0, 'New task'), (1, 'In progress'), (2, 'Done'), (255, 'Deleted')], default=0)),
                ('assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_assigned', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
