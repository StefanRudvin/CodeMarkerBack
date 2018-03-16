from rest_framework.test import force_authenticate, APIRequestFactory
from django.contrib.auth.models import User, Group
from app.tests.CustomTestCase import CustomTestCase
from app.views import CoursesList, CoursesDetail
from django.test import TestCase
from app.models import Course


class TestCourses(CustomTestCase):

    def test_get_courses(self):
        view = CoursesList.as_view()

        request = self.factory.get('/api/courses/')
        force_authenticate(request, user=self.student, token=self.student.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_courses_unauthenticated(self):
        view = CoursesList.as_view()

        request = self.factory.get('/api/courses/')
        response = view(request)

        self.assertEqual(response.status_code, 401)

    def test_post_courses(self):
        view = CoursesList.as_view()

        data = {
            'name': 'Test',
            'description': 'Test Description',
            'professor_id': self.professor.id
        }

        request = self.factory.post('/api/courses/', data)
        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(Course.objects.all()), 3)

    def test_post_courses_unauthenticated(self):
        view = CoursesList.as_view()

        request = self.factory.post('/api/courses/')
        response = view(request)

        self.assertEqual(response.status_code, 401)

    def test_post_courses_student(self):
        view = CoursesList.as_view()

        request = self.factory.post('/api/courses/')
        force_authenticate(request, user=self.student, token=self.student.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 403)

    def test_get_course(self):
        view = CoursesDetail.as_view()

        print(str(self.course1.id))

        request = self.factory.get('/api/courses/' + str(self.course1.id))
        print(request)
        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 200)













