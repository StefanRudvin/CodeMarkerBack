from rest_framework.test import force_authenticate
from app.tests.CustomTestCase import CustomTestCase
from app.views import CoursesList, CoursesDetail
from app.models import Course


class TestCourses(CustomTestCase):
    def test_get_courses(self):
        view = CoursesList.as_view()

        request = self.factory.get('/api/courses/')
        force_authenticate(request, user=self.student, token=self.student.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_courses_student(self):
        view = CoursesList.as_view()

        request = self.factory.get('/api/courses/')
        self.loginStudent(request)
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_courses_unauthenticated(self):
        view = CoursesList.as_view()

        request = self.factory.get('/api/courses/')
        response = view(request)

        self.assertEqual(response.status_code, 401)

    def test_create_courses(self):
        view = CoursesList.as_view()

        data = self.createCourseData()

        request = self.factory.post('/api/courses/', data)

        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(Course.objects.all()), 3)

    def test_create_courses_unauthenticated(self):
        view = CoursesList.as_view()

        request = self.factory.post('/api/courses/')
        response = view(request)

        self.assertEqual(response.status_code, 401)

    def test_create_courses_student(self):
        view = CoursesList.as_view()

        request = self.factory.post('/api/courses/')
        force_authenticate(request, user=self.student, token=self.student.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 403)

    def test_get_course(self):
        view = CoursesDetail.as_view()

        request = self.factory.get('/api/courses/' + str(self.course1.id) + '/')
        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request, pk=self.course1.id)

        self.assertEqual(response.status_code, 200)

    def test_get_course_student(self):
        view = CoursesDetail.as_view()

        request = self.factory.get('/api/courses/' + str(self.course1.id) + '/')
        self.loginStudent(request)
        response = view(request, pk=self.course1.id)

        self.assertEqual(response.status_code, 403)

    def test_get_course_unauthenticated(self):
        view = CoursesDetail.as_view()

        request = self.factory.get('/api/courses/' + str(self.course1.id) + '/')
        response = view(request, pk=self.course1.id)

        self.assertEqual(response.status_code, 401)

    def test_update_course(self):
        view = CoursesDetail.as_view()

        data = {
            'name': 'NewName'
        }

        request = self.factory.patch('/api/courses/' + str(self.course1.id) + '/', data)
        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request, pk=self.course1.id)

        course = Course.objects.get(pk=self.course1.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(course.name, 'NewName')

    def test_update_course_student(self):
        view = CoursesDetail.as_view()

        data = {
            'name': 'NewName'
        }

        request = self.factory.patch('/api/courses/' + str(self.course1.id) + '/', data)
        self.loginStudent(request)
        response = view(request, pk=self.course1.id)

        self.assertEqual(response.status_code, 403)

    def test_update_course_unauthenticated(self):
        view = CoursesDetail.as_view()

        data = {
            'name': 'NewName'
        }

        request = self.factory.patch('/api/courses/' + str(self.course1.id) + '/', data)
        response = view(request, pk=self.course1.id)

        self.assertEqual(response.status_code, 401)

    def test_delete_course(self):
        view = CoursesDetail.as_view()

        request = self.factory.delete('/api/courses/' + str(self.course1.id) + '/')
        self.loginProfessor(request)
        response = view(request, pk=self.course1.id)

        self.assertEqual(len(Course.objects.all()), 1)
        self.assertEqual(response.status_code, 204)

    def test_delete_course_student(self):
        view = CoursesDetail.as_view()

        request = self.factory.delete('/api/courses/' + str(self.course1.id) + '/')
        self.loginStudent(request)
        response = view(request, pk=self.course1.id)

        self.assertEqual(len(Course.objects.all()), 2)
        self.assertEqual(response.status_code, 403)

    def test_delete_course_unauthenticated(self):
        view = CoursesDetail.as_view()

        request = self.factory.delete('/api/courses/' + str(self.course1.id) + '/')
        response = view(request, pk=self.course1.id)

        self.assertEqual(len(Course.objects.all()), 2)
        self.assertEqual(response.status_code, 401)
