from django_mysql.models import EnumField
from django.utils import timezone
from django.conf import settings
from django.db import models
import datetime


# Create your models here.

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

    students = models.ManyToManyField(settings.AUTH_USER_MODEL, null=True, blank=True)

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)

    class Meta:
        ordering = ('created_at',)


class Resource(models.Model):
    filename = models.FileField(upload_to='resources/')
    content_type = models.CharField(max_length=400)

    status = EnumField(choices=['start', 'in_progress', 'complete'])

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
    content_type = models.CharField(max_length=400)

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
    description = models.CharField(max_length=1000, default="")
    additional_help = models.CharField(max_length=1000, default="")

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
    content_type = models.CharField(max_length=400)
    data = models.BinaryField(null=False)
    info = models.TextField(default='None')

    timeTaken = models.DecimalField(
        null=False, default=0, decimal_places=4, max_digits=4)

    status = EnumField(choices=['start', 'in_progress', 'complete'])
    result = EnumField(choices=['pass', 'fail', 'error'])
    language = EnumField(choices=['python2', 'python3', 'java', 'cpp', 'c', 'ruby'],
                         default='python2')

    marks = models.IntegerField()
    output = models.TextField

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
