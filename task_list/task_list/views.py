# -*- coding: utf-8 -*-
""" Views for Simple task manager """
import json

from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django import forms
from django.shortcuts import render_to_response
from django.db.models import Q
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from rq import Queue
from redis import Redis

from task_list.models import Task
from task_list.forms import TaskForm
from task_list.utils import send_email_status_updated


@staff_member_required
def tasks_main(request):
    """Main SPA view with task list"""
    task_form = TaskForm(initial={"owner": request.user, "assigned": request.user})
    context = {"username": request.user.username, "task_form": task_form}
    return render_to_response("tasks.html", context=context,
                              context_instance=RequestContext(request))


@staff_member_required
def task_list(request):
    """Ajax handler with filtered task list + task forms"""
    hide_done = request.GET.get('hide_done', 0)
    only_mine = request.GET.get('only_mine', 0)
    query = ~Q(status=Task.STATUS_DELETED)

    # -- filters for all/done, all/mine tasks
    if hide_done and hide_done == "1":
        query &= ~Q(status=Task.STATUS_DONE)
    if only_mine and only_mine == "1":
        query &= Q(owner=request.user)

    tasks = Task.objects.filter(query).order_by('status', '-pk').all()
    # -- add forms to "t_form" property (initialized by Task instances)
    res_tasks = []
    for tsk in tasks:
        r_task = model_to_dict(tsk)
        frm = TaskForm(instance=tsk)
        frm.fields["name"].widget = forms.TextInput(attrs={'class': 'tid_{}'.format(tsk.id)})
        frm.fields["description"].widget = forms.TextInput(attrs={'class': 'tid_{}'.format(tsk.id)})
        r_task["t_form"] = frm
        r_task["owner"] = tsk.owner.username
        r_task["owner_id"] = tsk.owner.id
        r_task["assigned"] = tsk.assigned.username
        r_task["assigned_id"] = tsk.assigned.id
        r_task["flavor_status"] = tsk.flavor_status
        res_tasks.append(r_task)
    context = {"tasks": res_tasks, "user": request.user}
    return render_to_response("task_rows.html", context=context,
                              context_instance=RequestContext(request))


@staff_member_required
def task_status(request):
    """Ajax handler to change status/start/delete task + check task owner rights"""
    set_status = request.GET.get('set_status', '')
    task_id = request.GET.get('task_id', 0)
    # -- check if task by id exists
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return HttpResponse(json.dumps({'error': 'no such task'}),
                            content_type='application/json')

    # -- check if status is correct
    if set_status not in dict(Task.STATUSES).values():
        return HttpResponse(json.dumps({'error': 'no such status {}'.format(set_status)}),
                            content_type='application/json')
    status_id = task.get_status_id_by_name(set_status)

    # -- check if user is owner for deleting
    if status_id == Task.STATUS_DELETED and task.owner != request.user:
        return HttpResponse(json.dumps({'error': 'no rights to delete task ' +
                                                 '{}'.format(task_id)}),
                            content_type='application/json')

    # -- check if new status differs from current
    if set_status == task.flavor_status():
        return HttpResponse(json.dumps({'error': 'can\'t change to the same status'}),
                            content_type='application/json')

    # -- update status
    if status_id in [Task.STATUS_DOING, Task.STATUS_DONE]:
        task.assigned = request.user
    task.status = status_id

    task.save()
    # -- send email about status update
    send_email_status_updated(request, task.assigned, set_status, edited=False)

    return HttpResponse(
        json.dumps({'ok': 'task {} status updated OK to {}'.format(task_id,
                                                                   set_status)}),
        content_type='application/json')


@staff_member_required
def task_edit(request):
    """Ajax handler to edit task name/description"""
    if request.method == "POST":
        kwargs = {}
        obj_id = request.POST.get("id")

        if obj_id:
            instance = Task.objects.get(id=obj_id)
            kwargs["instance"] = instance

        task_form = TaskForm(request.POST, **kwargs)
        if task_form.is_valid():
            task_form.save()
            assigned = User.objects.get(pk=task_form.cleaned_data['assigned'].id)

            # -- send email about task update
            set_status = task_form.cleaned_data['status']
            send_email_status_updated(request, assigned, set_status, edited=True)

            return HttpResponse(json.dumps({'ok': 'task saved successfully'}),
                                content_type='application/json')

        else:
            errors = task_form.errors
            return HttpResponse(json.dumps({'error': errors}), content_type='application/json')
    else:
        return HttpResponse("GET not implemented")
