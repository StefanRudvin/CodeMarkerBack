# CodeMarkerBack
Django Python backend for Codemarker, an application designed for the University of Aberdeen by students of the course CS3028 and CS3528.

## Setup

Requires Python 3.6.4 or above to run

Setup local mysql first in settings.py. Example:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'codemarker',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

Make sure that you actually have a database called codemarker and your user root (identified by password 'root') has access to the database.

- python manage.py makemigrations

- python manage.py migrate

- python manage.py runserver

**Optional**: Get Sample Data:
- python manage.py loaddata sampleData

username: Administrator  
password: Administrator
