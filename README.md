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

- virtualenv -p /usr/local/bin/python3 codemarker   - this needs to only run once

- source codemarker/bin/activate

- python manage.py makemigrations

- python manage.py migrate

- python manage.py runserver
