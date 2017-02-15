# -*- coding: utf-8 -*-
""" worker handling tasks to send emails """
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_list.settings")

from django.core.mail import EmailMessage
from django.conf import settings

def send_email(msg):
    msg.encoding = 'utf-8'
    msg.send()

