"""Tutorial URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from app import views


urlpatterns = [
    url(r'^codemarker/', include('app.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index),

    url(r'^obtain-auth-token/$', views.CustomObtainAuthToken.as_view()),

    url(r'^get-user/$', views.GetCurrentUserData.as_view()),

    url(r'^users/$', views.UsersList.as_view(), name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$',
        views.UsersDetail.as_view(), name='users-detail'),

    url(r'^courses/$', views.CoursesList.as_view(), name='courses-list'),
    url(r'^courses/(?P<pk>[0-9]+)/$',
        views.CoursesDetail.as_view(), name='courses-detail'),

    url(r'^courses/users/delete/$', views.CoursesUsersDestroy.as_view(),
        name='courses-users-delete'),

    url(r'^courses/users/add/$', views.CoursesUsersAdd.as_view(),
        name='courses-users-add'),

    url(r'^submissions/$', views.SubmissionsList.as_view(),
        name='submissions-list'),
    url(r'^submissions/(?P<pk>[0-9]+)/$',
        views.SubmissionsDetail.as_view(), name='submissions-detail'),

    url(r'^assessments/$', views.AssessmentsList.as_view(),
        name='assessments-list'),
    url(r'^assessments/(?P<pk>[0-9]+)/$',
        views.AssessmentsDetail.as_view(), name='assessments-detail'),

    url(r'^submissions/(?P<submission_id>\d+)/process/$',
        views.process_submission, name='submission-process'),

    url(r'^create_backup/$', views.CreateBackup.as_view()),
    url(r'^restore_backup/$', views.RestoreBackup.as_view()),

    url(r'^import_users/$', views.ImportUsers.as_view()),
]
