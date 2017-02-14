# -*- coding: utf-8 -*-
""" form validation """
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User

from task_list import models


class TaskForm(ModelForm):
    """ Task form additional validation """
    class Meta:
        """ meta """
        model = models.Task
        fields = '__all__'
        widgets = {'owner': forms.widgets.Select(attrs={'readonly': True})}
                                                        #'disabled': True})}

    def clean(self):
        if not self._errors:
            cleaned_data = super(TaskForm, self).clean()

            # -- check if owner and assigned users exist
            user_fields = ['owner', 'assigned']
            for u_field in user_fields:
                try:
                    user = User.objects.get(pk=cleaned_data.get(u_field).id)
                except User.DoesNotExist:
                    raise forms.ValidationError('Invalid {}'.format(u_field))

            return cleaned_data
