"""
Models information for all entities used in the system

@TeamAlpha 2018
CodeMarker
models.py
"""

import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone
from django_mysql.models import EnumField, ListCharField
# Create your models here.
from rest_framework.compat import MaxValueValidator, MinValueValidator


class Course(models.Model):
    name = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=400)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        related_name='professor'
    )

    def __str__(self):
        return 'Course: ' + str(self.id) + ' ' + str(self.name)

    students = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)

    class Meta:
        ordering = ('created_at',)
        permissions = (
            ("change_courses_users", "Can change courses_users"),
        )


class Resource(models.Model):
    filename = models.FileField(upload_to='resources/')

    status = EnumField(choices=['start', 'in_progress', 'complete'])
    language = EnumField(choices=['python2', 'python3', 'java', 'cpp', 'c', 'ruby'],
                         default='python2')

    def __str__(self):
        return 'Resource: ' + str(self.id) + '  ' + str(self.filename)

    assessment = models.ForeignKey(
        'Assessment',
        on_delete=models.CASCADE,
        null=False,
        default=None,
        related_name="resources"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InputGenerator(models.Model):
    filename = models.FileField(upload_to='input_generators/')
    language = EnumField(choices=['python2', 'python3', 'java', 'cpp', 'c', 'ruby'],
                         default='python2')

    assessment = models.ForeignKey(
        'Assessment',
        on_delete=models.CASCADE,
        null=False,
        default=None,
        related_name="input_generators"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Assessment(models.Model):
    name = models.CharField(max_length=400, null=False)
    #description = models.CharField(max_length=1000, default="")
    #additional_help = models.CharField(max_length=1000, default="")
    description = models.TextField(default="")
    additional_help = models.TextField(default="")
    deadline = models.DateTimeField(blank=False)
    static_input = models.BooleanField(default=False)
    dynamic_input = models.BooleanField(default=False)
    num_of_static = models.IntegerField(default=0)

    def __str__(self):
        return 'Assessment: ' + str(self.id) + '  ' + str(self.name)

    languages = ListCharField(
        base_field=models.CharField(max_length=10),
        size=10,
        max_length=(10 * 11),
        null=True
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        default=None,
        related_name="resources",
        null=True
    )

    course = models.ForeignKey(
        Course,
        null=False,
        related_name="assessments"
    )

    input_generator = models.ForeignKey(
        InputGenerator,
        on_delete=models.CASCADE,
        default=None,
        related_name="input_generators",
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%d %s %s' % (self.id, self.name, self.description)


class Submission(models.Model):
    filename = models.FileField(upload_to='submissions/')
    info = models.TextField(default='None')

    timeTaken = models.DecimalField(
        null=False, default=0, decimal_places=4, max_digits=4)

    late = models.BooleanField(default=False)

    status = EnumField(choices=['start', 'in_progress', 'complete', 'late'])
    result = EnumField(choices=['pass', 'fail', 'error'])
    language = EnumField(choices=['python2', 'python3', 'java', 'cpp', 'c', 'ruby'],
                         default='python2')

    marks = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    output = models.TextField

    def __str__(self):
        return 'Submission: ' + str(self.id) + '  ' + str(self.filename)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False
    )
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        null=False,
        related_name="submissions"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
