from rest_framework.test import force_authenticate, APIRequestFactory
from django.contrib.auth.models import User, Group
from app.views import CoursesList, CoursesDetail
from django.test import TestCase
from app.models import Course
from django.test import TestCase

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

        self.factory = APIRequestFactory()