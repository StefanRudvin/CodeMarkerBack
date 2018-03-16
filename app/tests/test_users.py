from rest_framework.test import force_authenticate
from app.tests.CustomTestCase import CustomTestCase
from app.views import UsersList, UsersDetail
from django.contrib.auth.models import User


class TestUsers(CustomTestCase):

    @staticmethod
    def getApiUrl():
        return '/api/users'

    def test_get_users(self):
        view = UsersList.as_view()

        request = self.factory.get(self.getApiUrl())
        force_authenticate(request, user=self.student, token=self.student.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_users_student(self):
        view = UsersList.as_view()

        request = self.factory.get(self.getApiUrl())
        self.loginStudent(request)
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_users_unauthenticated(self):
        view = UsersList.as_view()

        request = self.factory.get(self.getApiUrl())
        response = view(request)

        self.assertEqual(response.status_code, 401)

    def test_create_users(self):
        self.assertEqual(len(User.objects.all()), 3)

        view = UsersList.as_view()

        data = self.createUserData()

        request = self.factory.post(self.getApiUrl(), data)

        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(User.objects.all()), 4)

    def test_create_courses_unauthenticated(self):
        view = UsersList.as_view()

        request = self.factory.post(self.getApiUrl())
        response = view(request)

        self.assertEqual(response.status_code, 401)

    def test_create_users_student(self):
        view = UsersList.as_view()

        request = self.factory.post(self.getApiUrl())
        force_authenticate(request, user=self.student, token=self.student.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 403)

    def test_get_user(self):
        view = UsersDetail.as_view()

        request = self.factory.get(self.getApiUrl() + str(self.student.id) + '/')
        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request, pk=self.student.id)

        self.assertEqual(response.status_code, 200)

    def test_get_user_student(self):
        view = UsersDetail.as_view()

        request = self.factory.get(self.getApiUrl() + str(self.admin.id) + '/')
        self.loginStudent(request)
        response = view(request, pk=self.admin.id)

        self.assertEqual(response.status_code, 403)

    def test_get_user_unauthenticated(self):
        view = UsersDetail.as_view()

        request = self.factory.get(self.getApiUrl() + str(self.student.id) + '/')
        response = view(request, pk=self.student.id)

        self.assertEqual(response.status_code, 401)

    def test_update_user(self):
        view = UsersDetail.as_view()

        data = {
            'username': 'NewName'
        }

        request = self.factory.patch(self.getApiUrl() + str(self.student.id) + '/', data)
        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request, pk=self.student.id)

        user = User.objects.get(pk=self.student.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.username, 'NewName')

    def test_update_user_student(self):
        view = UsersDetail.as_view()

        data = {
            'name': 'NewName'
        }

        request = self.factory.patch(self.getApiUrl() + str(self.student.id) + '/', data)
        self.loginStudent(request)
        response = view(request, pk=self.student.id)

        self.assertEqual(response.status_code, 403)

    def test_update_user_unauthenticated(self):
        view = UsersDetail.as_view()

        data = {
            'name': 'NewName'
        }

        request = self.factory.patch(self.getApiUrl() + str(self.student.id) + '/', data)
        response = view(request, pk=self.student.id)

        self.assertEqual(response.status_code, 401)

    def test_delete_user(self):
        self.assertEqual(len(User.objects.all()), 3)
        view = UsersDetail.as_view()

        request = self.factory.delete(self.getApiUrl() + str(self.student.id) + '/')
        self.loginProfessor(request)
        response = view(request, pk=self.student.id)

        self.assertEqual(len(User.objects.all()), 2)
        self.assertEqual(response.status_code, 204)

    def test_delete_user_student(self):

        self.assertEqual(len(User.objects.all()), 3)

        view = UsersDetail.as_view()

        request = self.factory.delete(self.getApiUrl() + str(self.student.id) + '/')
        self.loginStudent(request)
        response = view(request, pk=self.student.id)

        self.assertEqual(response.status_code, 403)

        self.assertEqual(len(User.objects.all()), 3)

    def test_delete_user_unauthenticated(self):
        view = UsersDetail.as_view()

        request = self.factory.delete(self.getApiUrl() + str(self.student.id) + '/')
        response = view(request, pk=self.student.id)

        self.assertEqual(len(User.objects.all()), 3)
        self.assertEqual(response.status_code, 401)
