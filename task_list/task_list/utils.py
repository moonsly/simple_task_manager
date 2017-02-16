# -*- coding: utf-8 -*-
""" utils with enqueing emails """
import re
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_list.settings")

from rq import Queue
from redis import Redis
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from task_list.mail_worker import send_email
from task_list.models import Task


def send_email_status_updated(request, user, new_status, edited=False):
    """ build email and enqueue send_email task to redis queue worker """
    redis_conn = Redis()
    domain = get_current_site(request).domain

    # -- email template and it's values
    msg_text = """Hello, {username}!\n
Your colleague assigned the task to you and udpated status of the task to {status}.\n
{edited}\n\nTo check out your new task please go to {domain}\n\n
--\n\n
This is automatic letter from Simple task manager\n"""

    if re.search(r'^\d+$', str(new_status)):
        new_status = dict(Task.STATUSES)[int(new_status)]
    tmpl_args = {"username": user.username, "status": new_status, "domain": domain, "edited": ""}
    if edited:
        tmpl_args["edited"] = "Also the task's name or description were changed."
    msg_text = msg_text.format(**tmpl_args)
    
    msg = EmailMessage(
        "Notification from Simple task manager",
        msg_text,
        settings.DEFAULT_FROM_EMAIL,
        (user.email,),
    )

    q = Queue('send_email', connection=redis_conn)
    q.enqueue(send_email, msg)

