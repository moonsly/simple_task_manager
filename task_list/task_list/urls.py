"""task_list URL Configuration"""

from django.conf.urls import url
from django.contrib import admin

from task_list.views import tasks_main, task_list, task_status, task_edit

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', tasks_main, name='tasks'),
    url(r'^task-list/', task_list, name='task-list'),
    url(r'^task-status/', task_status, name='task-status'),
    url(r'^task-edit/', task_edit, name='task-edit'),
]
