from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import Submission, Assessment, InputGenerator, Resource, Course

admin.site.register(Submission)
admin.site.register(Assessment)
admin.site.register(InputGenerator)
admin.site.register(Course)
admin.site.register(Resource)
