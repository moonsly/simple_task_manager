# -*- coding: utf-8 -*-
""" Task model, helper methods """
from django.db.models import Model, CharField, ForeignKey, TextField, DateTimeField,\
                             PositiveIntegerField
from django.contrib.auth.models import User


class Task(Model):
    """ Model for Task """

    name = CharField(max_length=50, unique=True)
    description = TextField(blank=True, null=True)
    owner = ForeignKey(User, related_name="user_owner")
    assigned = ForeignKey(User, related_name="user_assigned")
    updated = DateTimeField(auto_now_add=True)

    # -- add more task statuses if needed
    STATUS_CREATED = 0
    STATUS_DOING = 1
    STATUS_DONE = 2
    STATUS_DELETED = 255
    STATUSES = (
        (STATUS_CREATED, 'New'),
        (STATUS_DOING, 'Doing'),
        (STATUS_DONE, 'Done'),
        (STATUS_DELETED, 'Deleted'),
    )
    status = PositiveIntegerField(choices=STATUSES, default=STATUS_CREATED)

    def flavor_status(self):
        """ return named status """
        return dict(Task.STATUSES)[self.status]

    def get_status_id_by_name(self, name):
        """ get status name by id """
        status_id = dict((v, k) for k, v in dict(self.STATUSES).items())
        return status_id.get(name)

    def __unicode__(self):
        """ unicode """
        return self.name
