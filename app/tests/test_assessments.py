from rest_framework.test import force_authenticate, APIRequestFactory
from django.contrib.auth.models import User, Group
from app.tests.CustomTestCase import CustomTestCase
from app.views import CoursesList, CoursesDetail, AssessmentsList, AssessmentsDetail
from django.test import TestCase, utils
from app.models import Course


class TestCourses(CustomTestCase):

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

        data = {
            'name': 'Test',
            'description': 'Test Description',
            'additional_help' : 'Additional help',
            'course_id': self.course1.id,
            'deadline': utils.date.today()
        }

        request = self.factory.post('/api/assessments/', data)
        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request)
        print(response)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(Course.objects.all()), 3)

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

        print(str(self.course1.id))

        request = self.factory.get('/api/assessments/' + str(self.course1.id))
        print(request)
        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 200)













