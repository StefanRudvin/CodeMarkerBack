import os

from rest_framework.test import force_authenticate, APIRequestFactory
from django.contrib.auth.models import User, Group
from app.tests.CustomTestCase import CustomTestCase
from app.views import CoursesList, CoursesDetail, AssessmentsList, AssessmentsDetail
from django.utils.timezone import now
from app.models import Course, Assessment
import json


class TestAssessments(CustomTestCase):
    def test_get_assessments(self):
        view = AssessmentsList.as_view()

        request = self.factory.get('/api/assessments/')
        force_authenticate(request, user=self.student, token=self.student.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_assessments_unauthenticated(self):
        view = AssessmentsList.as_view()

        request = self.factory.get('/api/assessments/')
        response = view(request)

        self.assertEqual(response.status_code, 401)

    def test_post_assessments(self):
        view = AssessmentsList.as_view()

        with open('./demo/Python3/generator.py') as generator:
            with open('./demo/Python3/resource.py') as resource:
                data = self.createAssessmentData(resource, generator)

                request = self.factory.post('/api/assessments/', data)

                force_authenticate(request, user=self.professor, token=self.professor.auth_token)
                response = view(request)
                print(response)

                self.assertEqual(response.status_code, 201)
                self.assertEqual(len(Assessment.objects.all()), 3)

    def test_post_assessments_unauthenticated(self):
        view = AssessmentsList.as_view()

        request = self.factory.post('/api/assessments/')
        response = view(request)

        self.assertEqual(response.status_code, 401)

    def test_post_assessments_student(self):
        view = AssessmentsList.as_view()

        request = self.factory.post('/api/assessments/')
        force_authenticate(request, user=self.student, token=self.student.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 403)

    def test_get_assessment(self):
        view = AssessmentsDetail.as_view()

        print(self.course1)

        request = self.factory.get('/api/assessments/' + str(self.assessment1.id) + '/')
        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request, pk=self.assessment1.id)

        self.assertEqual(response.status_code, 200)
