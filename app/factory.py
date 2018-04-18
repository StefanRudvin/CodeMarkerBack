"""
Module containing creators for subsequent elements, such as assessments or submissions.
Adheres to 'factory' architectural pattern.

Factories to create new resources with lengthy methods.

@TeamAlpha 2018
CodeMarker
factory.py
"""

import json
import logging
import os

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.db import DataError
from django.http import (HttpResponseBadRequest, HttpResponseForbidden)
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.response import Response

from app.backup_service import create_backup
from app.models import Assessment, Course, InputGenerator, Resource, Submission

# Get an instance of a logger
logger = logging.getLogger(__name__)


def assessment_creator(self, serializer):
    """Method responsible for creating new assessments

    Raises:
        MultiValueDictKeyError -- Raised when not enough arguments have been passed

    Returns:
        HttpResponse -- Whether resource has been successfully created or not
    """

    try:
        user = self.request.user
        name = self.request.POST.get("name", "")
        course_id = self.request.POST.get("course_id", "")
        description = self.request.POST.get("description", "")
        additional_help = self.request.POST.get("additional_help", "")

        deadline = self.request.POST.get('deadline', "")

        dynamic_input = self.request.POST["dynamicInput"]
        static_input = self.request.POST["staticInput"]

        languages = [x for x in json.loads(
            self.request.POST.get('languages', ""))]
        selected_language = self.request.POST.get('selected_language', "")
        num_of_static = int(self.request.POST.get('numOfStatic', ""))

        if static_input == "true":
            for i in range(int(num_of_static)):
                if 'inputFile'+str(i) not in self.request.FILES or 'outputFile'+str(i) not in self.request.FILES:
                    raise MultiValueDictKeyError
    except MultiValueDictKeyError:
        return HttpResponseBadRequest("Looks like you have an empty field or an unknown file type.")
    except Exception as e:
        logger.error(e)
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
        deadline=deadline,
        static_input=json.loads(static_input),
        dynamic_input=json.loads(dynamic_input),
        num_of_static=num_of_static)

    assessment.save()

    if static_input == "true":
        for i in range(int(num_of_static)):
            os.makedirs(os.path.join(settings.MEDIA_ROOT,
                                     str(assessment.id), 'static_inputs'), exist_ok=True)
            os.makedirs(os.path.join(settings.MEDIA_ROOT,
                                     str(assessment.id), 'expected_static_outputs'), exist_ok=True)

            fs = FileSystemStorage(location=os.path.join(
                settings.MEDIA_ROOT, str(assessment.id), 'static_inputs'))
            static_file = self.request.FILES['inputFile'+str(i)]
            fs.save(str(i), static_file)

            fs = FileSystemStorage(location=os.path.join(
                settings.MEDIA_ROOT, str(assessment.id), 'expected_static_outputs'))
            static_file = self.request.FILES['outputFile'+str(i)]
            fs.save(str(i), static_file)

    if dynamic_input == "true":

        resource_file = self.request.FILES['resource']

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

    return Response(assessment.id, 201)


def course_creator(self, serializer):
    """
    Dummy method for course creation, for future reference
    """

    pass


def submission_creator(self, serializer):
    """Method for creating new submissions

    Arguments:
        serializer - passed from the views class, contains POST information

    Returns:
        HttpResponse - whether creation was successful or not
    """

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
        logger.error(e)
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

    return Response(submission.id, 201)


def import_users(request):
    """Given an uploaded CSV file containing list of users, import them into DB

    Arguments:
        request - request containing the uploaded CSV file

    Returns:
        request -- Whether the import was successful or not
    """

    # Create backup of the current userbase before import
    create_backup()

    # Parse uploaded CSV file
    csvfile = request.FILES.get("csv").read().decode("utf-8")
    logger.error(csvfile)
    # Iterate the CSV file for entries
    for row in csvfile.splitlines():
        userdata = row.split(',')

        # Delete duplicated users first
        try:
            user = User.objects.get(username=userdata[2])
            user.delete()
        except ObjectDoesNotExist:
            logger.debug("Requested user doesn't exist. Ignoring")

        # Create and save new user based on the provided information in CSV
        user = User.objects.create_user(first_name=userdata[0],
                                        last_name=userdata[1],
                                        username=userdata[2],
                                        email=userdata[3],
                                        password=userdata[4])
        user.save()

        # Add student to the group
        group = Group.objects.get(name='student')
        group.user_set.add(user)
        group.save()

        courses = userdata[5].split()
        # Add student to all courses specified in the CSV file
        try:
            for course in courses:
                course_model = Course.objects.get(name=course)
                course_model.students.add(user)
                course_model.save()
        except ObjectDoesNotExist:
            # Something went wrong, report the issue and halt the import
            return Response("One of the courses doesn't exist!", 400)

    # All was fine, return OK
    return Response(status=200)
