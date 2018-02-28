from app.models import Course, Assessment, Submission, Resource, InputGenerator
from django.utils.datastructures import MultiValueDictKeyError
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from rest_framework.response import Response
from django.conf import settings
from django.db import DataError
import json
import os


"""
    Factories to create new resources with lengthy methods.
"""


def assessment_creator(self, serializer):
    try:
        user = self.request.user
        name = self.request.POST.get("name", "")
        course_id = self.request.POST.get("course_id", "")
        description = self.request.POST.get("description", "")
        additional_help = self.request.POST.get("additional_help", "")
        resource_file = self.request.FILES['resource']
        languages = [x for x in json.loads(
            self.request.POST.get('languages', ""))]
        selected_language = self.request.POST.get('selected_language', "")
        deadline = self.request.POST.get('deadline', "")

    except MultiValueDictKeyError:
        return HttpResponseBadRequest("Looks like you have an empty field or an unknown file type.")
    except Exception as e:
        print(e)
        return HttpResponseBadRequest("Unexpected error.")

    if name == "" or description == "":
        return HttpResponseBadRequest("Looks like you have an empty field.")

    if not user.is_staff:
        return HttpResponseForbidden("You are not allowed to create assessments")

    course = Course.objects.get(pk=course_id)

    assessment = Assessment(
        name=name,
        description=description,
        additional_help=additional_help,
        course=course,
        languages=languages,
        deadline=deadline)

    assessment.save()

    resource = Resource(
        filename=resource_file.name,
        status="start",
        assessment=assessment,
        language=selected_language)
    resource.save()

    os.makedirs(os.path.join(settings.MEDIA_ROOT,
                             str(assessment.id), 'model_solutions', str(resource.id)), exist_ok=True)
    fs = FileSystemStorage(location=os.path.join(
        settings.MEDIA_ROOT, str(assessment.id), 'model_solutions', str(resource.id)))

    fs.save(resource_file.name, resource_file)

    if self.request.FILES['input_generator']:
        input_generator_file = self.request.FILES['input_generator']

        input_generator = InputGenerator(
            filename=input_generator_file.name,
            assessment=assessment,
            language=selected_language)
        input_generator.save()

        os.makedirs(os.path.join(settings.MEDIA_ROOT,
                                 str(assessment.id), 'input_generators', str(input_generator.id)),
                    exist_ok=True)
        fs = FileSystemStorage(location=os.path.join(
            settings.MEDIA_ROOT, str(assessment.id), 'input_generators', str(input_generator.id)))

        fs.save(input_generator_file.name, input_generator_file)

        assessment.input_generator = input_generator

    assessment.resource = resource

    assessment.save()

    return Response(assessment.id)


def course_creator(self, serializer):
    pass


def submission_creator(self, serializer):
    try:
        assessment_id = self.request.POST['assessment_id']
        language = self.request.POST['language']
        submission_file = self.request.FILES['submission']
        late = self.request.POST['late']
    except MultiValueDictKeyError:
        return HttpResponseBadRequest("Looks like you have an empty upload field.")
    except DataError:
        return HttpResponseBadRequest("Looks like you have an empty dropdown field.")
    except Exception as e:
        print(e)
        return HttpResponseBadRequest("Unexpected error.")

    if language == "undefined":
        return HttpResponseBadRequest("Looks like you have an empty language field.")

    assessment = Assessment.objects.get(id=assessment_id)
    course = Course.objects.get(id=assessment.course_id)

    if self.request.user not in course.students.all():
        return HttpResponseForbidden("You cannot submit to a course you are not enrolled in.")

    submission = Submission(
        filename=submission_file.name,
        status="start",
        result="fail",
        info="Awaiting result...",
        marks=0,
        user_id=self.request.user.id,
        assessment_id=assessment_id,
        timeTaken=0,
        language=language,
        late=late)
    submission.save()

    os.makedirs(os.path.join(settings.MEDIA_ROOT,
                             assessment_id, 'submissions', str(submission.id)), exist_ok=True)
    fs = FileSystemStorage(location=os.path.join(
        settings.MEDIA_ROOT, assessment_id, 'submissions', str(submission.id)))

    filename = fs.save(submission_file.name, submission_file)
    uploaded_file_url = fs.url(filename)

    return Response(submission.id)
