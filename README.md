Simple task manager on Python3, Django 1.9, jquery UI.
========

Redmine-like simple task manager, without separate projects, access rights - shared task flow for all registered users.
To add new members - django admin needs to login, add user and mark him as staff.
Admin also able to edit all the tasks in django admin.

Staff user can create new tasks, edit/delete their tasks, start/make done any existing tasks with changing assigned field to him.

Add task form is implemented via jquery UI, edit task is implemented as ajax form in the tasks table.
Email messages queue is implemented using redis and python-rq.

Extra features
========

Added email notification queue via redis-queue. To send emails - admin should set correct emails for your users and uncomment lines in the end of settings.py

INSTALL
========

1) Install python3.5

2) Make new virtualenv with python3:

`virtualenv -p python3 ./env/`

3) Clone project to virtualenv:

```
cd env
git clone https://github.com/moonsly/simple_task_manager.git ./code
```

4) Install dependencies:

```
cd code
pip install -r ./requirements.txt
```

5) In Mysql create user, database and configure them in settings.py:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'task_list',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}
```

6) Run migrate to make initial DB structure:

`python ./manage.py migrate task_list`

7) Create superuser to enter django admin:

`python ./manage.py createsuperuser`

8) Start server in debug mode:

`python ./manage.py runserver 0.0.0.0:8080`

9) Enter django admin at /8080, create new users and then tasks on / , mark them Doing/Done, delete, edit, enjoy :)
