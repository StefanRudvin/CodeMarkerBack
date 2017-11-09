from django.http import HttpResponse
from codemarker.models import Course, Assessment

from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse

from codemarker.serializers import CourseSerializer, AssessmentSerializer


def index(request):
    return HttpResponse("Hello world. You're at the codemarker index.")


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
