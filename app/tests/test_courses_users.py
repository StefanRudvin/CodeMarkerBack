from app.tests.CustomTestCase import CustomTestCase
from app.views import CoursesUsersDestroy, CoursesUsersAdd


class TestCoursesUsers(CustomTestCase):

    def test_add_courses_users(self):

        self.assertTrue(self.student not in self.course1.students.all())

        view = CoursesUsersAdd.as_view()

        data = {
            'course_id': self.course1.id,
            'user_id': self.student.id
        }

        request = self.factory.post('api/courses/users/add/', data)
        self.loginProfessor(request)
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.student in self.course1.students.all())

    def test__add_courses_users_student(self):
        view = CoursesUsersAdd.as_view()

        request = self.factory.post('api/courses/users/add/')
        self.loginStudent(request)
        response = view(request)

        self.assertEqual(response.status_code, 403)

    def test_add_courses_users_unauthorized(self):
        view = CoursesUsersAdd.as_view()

        request = self.factory.post('api/courses/users/add/')
        response = view(request)

        self.assertEqual(response.status_code, 401)

    def test_remove_courses_users(self):
        self.assertTrue(self.student not in self.course1.students.all())

        self.course1.students.add(self.student)

        self.assertTrue(self.student in self.course1.students.all())

        data = {
            'course_id': self.course1.id,
            'user_id': self.student.id
        }

        view = CoursesUsersDestroy.as_view()

        request = self.factory.post('api/courses/users/delete/', data)
        self.loginProfessor(request)
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.student not in self.course1.students.all())

    def test_remove_courses_users_student(self):

        view = CoursesUsersDestroy.as_view()

        request = self.factory.post('api/courses/users/delete/')
        self.loginStudent(request)
        response = view(request)

        self.assertEqual(response.status_code, 403)

    def test_remove_courses_users_unauthorized(self):
        view = CoursesUsersDestroy.as_view()

        request = self.factory.post('api/courses/users/delete/')
        response = view(request)

        self.assertEqual(response.status_code, 401)
