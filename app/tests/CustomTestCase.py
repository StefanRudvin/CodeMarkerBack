from rest_framework.test import force_authenticate, APIRequestFactory
from django.contrib.auth.models import User, Group
from app.views import CoursesList, CoursesDetail
from django.test import TestCase
from app.models import Course, Assessment
from django.test import TestCase
from django.utils.timezone import now
import json

class CustomTestCase(TestCase):
    fixtures = ['testData.json']

    @classmethod
    def setUpTestData(self):
        # Set up data for the whole TestCase

        admin_group = Group.objects.get(name='administrator')
        professor_group = Group.objects.get(name='professor')

        self.professor = User.objects.create(
            username="staff",
            is_staff=True)
        professor_group.user_set.add(self.professor)
        self.professor.set_password('staff')
        self.professor.save()

        self.student = User.objects.create(
            username="student",
        )
        self.student.set_password('student')
        self.student.save()

        self.admin = User.objects.create(
            username="Admin",
            is_superuser=True
        )
        admin_group.user_set.add(self.admin)
        self.admin.set_password('admin')
        self.admin.save()

        self.course1 = Course.objects.create(
            professor=self.professor
        )
        self.course2 = Course.objects.create(
            professor=self.professor
        )

        self.assessment1 = Assessment.objects.create(
            name='testAssessment',
            deadline=now(),
            course=self.course1
        )

        self.assessment1 = Assessment.objects.create(
            name='testAssessment2',
            deadline=now(),
            course=self.course1
        )

        self.factory = APIRequestFactory()

    def createAssessmentData(self, resource, generator):
        return {
                    'name': 'Test',
                    'description': 'Test Description',
                    'additional_help': 'Additional help',
                    'course_id': self.course1.id,
                    'deadline': now(),
                    'dynamicInput': "true",
                    'resource': resource,
                    'input_generator': generator,
                    'staticInput': "false",
                    'numOfStatic': 0,
                    'selected_language': 'Python3',
                    'languages': json.dumps(['Python2']),
                }