from django.http import HttpResponse
from codemarker.models import Course, Assessment, Submission
from codemarker.forms import SubmissionForm

from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from codemarker.SubmissionProcessor import processSubmission
from django.core import serializers as djangoserializers
import json

from codemarker.serializers import CourseSerializer, AssessmentSerializer, SubmissionSerializer


def index(request):
    return HttpResponse("Hello world. You're at the codemarker index.")

@csrf_exempt
def assessmentsUpload(request, assessmentId):

    if request.method == 'POST' and request.FILES['submission']:
        myfile = request.FILES['submission']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        submission = Submission(
            filename=filename,
            content_type="python",
            status="start",
            result="fail",
            marks=0,
            user_id=1,
            assessment_id=assessmentId,
            timeTaken=0)
        submission.save()

        return HttpResponse(submission.id)


def submissionsProcess(request, submission_id):
    return HttpResponse(processSubmission(submission_id), content_type='text/plain')


class CoursesList(generics.ListCreateAPIView):
    """
        List all courses.
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CoursesDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single course.
        :rtype: Course
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class AssessmentsList(generics.ListCreateAPIView):
    """
        List all assessments.
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AssessmentsDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single Assessment.
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer


class SubmissionsList(generics.ListCreateAPIView):
    """
        List all submissions.
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubmissionsDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single submission.
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
