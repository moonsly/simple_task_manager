# -*- coding: utf-8 -*-
from django.test import TestCase, Client, modify_settings
from django.contrib.auth.models import User

from task_list.models import Task

ADMIN = { "username": "test_admin", "password": "q1w2e3r4" }
STAFF = { "username": "test_staff", "password": "q1w2e3r4" }
NON_STAFF = { "username": "non_staff", "password": "q1w2e3r4" }


class AccessRightsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.admin = User.objects.create_superuser(ADMIN["username"], email="test@admin.com",
                                                  password=ADMIN["password"])

        cls.staff = User.objects.create_user(STAFF["username"], email="test@staff.com",
                                             password=STAFF["password"])
        cls.staff.is_staff=True
        cls.staff.save()

        cls.non_staff = User.objects.create_user(NON_STAFF["username"], email="test@nonstaff.com",
                                                 password=NON_STAFF["password"])

        Task.objects.create(pk=1, name="test_admin owner, task1", owner=cls.admin, assigned=cls.admin)
        Task.objects.create(pk=2, name="test_admin owner, task2", owner=cls.admin, assigned=cls.admin)
        Task.objects.create(pk=3, name="test_staff owner, task3", owner=cls.staff, assigned=cls.staff)
        Task.objects.create(pk=4, name="test_staff owner, task4", owner=cls.staff, assigned=cls.staff)

        cls.client = Client()


    def test1_login_ok(self):
        # check if login with correct data works
        resp = self.client.post('/admin/login/?next=/',
                                {'username': ADMIN["username"], 'password': ADMIN["password"]})
        assert resp.status_code == 302 and resp.content == b''

        resp_main = self.client.get('/')
        assert b"Welcome to Simple task manager" in resp_main.content

        self.client.get('/admin/logout/')


    def test2_login_wrong_creds(self):
        # Check if login with incorrect data works correctly
        resp = self.client.post('/admin/login/?next=/',
                                {'username': ADMIN["username"], 'password': ADMIN["password"] + "1"})

        assert resp.status_code == 200 and b"Log in | Django site admin" in resp.content

        resp_main = self.client.get('/')
        assert resp_main.status_code == 302 and resp_main.content == b''

        self.client.get('/admin/logout/')


    def test3_login_non_staff(self):
        # Check if login with incorrect data works correctly
        resp = self.client.post('/admin/login/?next=/',
                                {'username': NON_STAFF["username"], 'password': NON_STAFF["password"]})

        assert resp.status_code == 200 and b"Log in | Django site admin" in resp.content

        resp_main = self.client.get('/')
        assert resp_main.status_code == 302 and resp_main.content == b''

        self.client.get('/admin/logout/')


    def test4_delete_my_own_task(self):
        resp = self.client.post('/admin/login/?next=/',
                                {'username': ADMIN["username"], 'password': ADMIN["password"]})

        assert resp.status_code == 302 and resp.content == b''

        resp_main = self.client.get('/')
        assert b"Welcome to Simple task manager" in resp_main.content

        resp_del = self.client.get("/task-status/?task_id=1&set_status=Deleted")
        assert b"status updated OK to Deleted" in resp_del.content

        self.client.get('/admin/logout/')


    def test5_delete_not_mine_task(self):
        resp = self.client.post('/admin/login/?next=/',
                                {'username': ADMIN["username"], 'password': ADMIN["password"]})

        assert resp.status_code == 302 and resp.content == b''
        
        resp_main = self.client.get('/')
        assert b"Welcome to Simple task manager" in resp_main.content

        resp_del = self.client.get("/task-status/?task_id=3&set_status=Deleted")
        assert b"no rights to delete task" in resp_del.content

        self.client.get('/admin/logout/')


    def test6_update_status_of_my_task(self):
        resp = self.client.post('/admin/login/?next=/',
                                {'username': ADMIN["username"], 'password': ADMIN["password"]})

        assert resp.status_code == 302 and resp.content == b''
        
        resp_main = self.client.get('/')
        assert b"Welcome to Simple task manager" in resp_main.content

        resp_st = self.client.get("/task-status/?task_id=2&set_status=Doing")
        assert b"status updated OK to Doing" in resp_st.content

        # -- check error msg on updating to the same status
        resp_st = self.client.get("/task-status/?task_id=2&set_status=Doing")
        assert b"can't change to the same status" in resp_st.content

        self.client.get('/admin/logout/')


    def test7_update_status_of_foreign_task(self):
        resp = self.client.post('/admin/login/?next=/',
                                {'username': ADMIN["username"], 'password': ADMIN["password"]})

        assert resp.status_code == 302 and resp.content == b''
        
        resp_main = self.client.get('/')
        assert b"Welcome to Simple task manager" in resp_main.content

        resp_del = self.client.get("/task-status/?task_id=3&set_status=Doing")
        assert b"status updated OK to Doing" in resp_del.content

        task3 = Task.objects.get(pk=3)
        assert task3.assigned == self.admin and task3.owner == self.staff

        self.client.get('/admin/logout/')
