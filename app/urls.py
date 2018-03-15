import django.conf.urls

from . import views

urlpatterns = [
    django.conf.urls.url(r'$', views.index, name='index'),
]


