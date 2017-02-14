# -*- coding: utf-8 -*-
""" administration config for Task """
from django.contrib import admin
from django.conf.locale.ru import formats as ru_formats
from task_list.models import Task

ru_formats.DATETIME_FORMAT = "d.m.Y H:i:s"


class TaskAdmin(admin.ModelAdmin):
    """ Task admin module """
    search_fields = ('id', )
    list_display = (
        'id',
        'name',
        'description',
        'owner',
        'assigned',
        'status',
        'updated',
    )

admin.site.register(Task, TaskAdmin)
