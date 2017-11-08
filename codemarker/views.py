from django.http import HttpResponse
from codemarker.models import Course

from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse

from codemarker.serializers import CourseSerializer


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
        List all courses.
        :rtype: object
    """

    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.all().filter(user=self.request.user)