from rest_framework.test import force_authenticate
from app.tests.CustomTestCase import CustomTestCase
from app.views import SubmissionsList, SubmissionsDetail
from app.models import Submission


class TestSubmissions(CustomTestCase):

    @staticmethod
    def getApiUrl():
        return '/submissions'

    def test_get_submissions(self):
        view = SubmissionsList.as_view()

        request = self.factory.get(self.getApiUrl())
        force_authenticate(request, user=self.student, token=self.student.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_submissions_student(self):
        view = SubmissionsList.as_view()

        request = self.factory.get(self.getApiUrl())
        self.loginStudent(request)
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_submissions_unauthenticated(self):
        view = SubmissionsList.as_view()

        request = self.factory.get(self.getApiUrl())
        response = view(request)

        self.assertEqual(response.status_code, 401)

    def test_create_submissions(self):
        view = SubmissionsList.as_view()

        self.course1.students.add(self.professor)

        with open('./demo/Python3/resource.py') as resource:

            data = self.createSubmissionData(resource)

            request = self.factory.post(self.getApiUrl(), data)

            self.loginProfessor(request)

            response = view(request)

            self.assertEqual(response.status_code, 201)
            self.assertEqual(len(Submission.objects.all()), 3)

    def test_create_submissions_unauthenticated(self):
        view = SubmissionsList.as_view()

        request = self.factory.post(self.getApiUrl())
        response = view(request)

        self.assertEqual(response.status_code, 401)

    def test_create_submissions_student(self):
        view = SubmissionsList.as_view()

        request = self.factory.post(self.getApiUrl())
        force_authenticate(request, user=self.student, token=self.student.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 403)

    def test_get_submission(self):
        view = SubmissionsDetail.as_view()

        request = self.factory.get(self.getApiUrl() + str(self.submission1.id) + '/')
        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request, pk=self.submission1.id)

        self.assertEqual(response.status_code, 200)

    def test_get_submission_student(self):
        view = SubmissionsDetail.as_view()

        request = self.factory.get(self.getApiUrl() + str(self.submission1.id) + '/')
        self.loginStudent(request)
        response = view(request, pk=self.submission1.id)

        self.assertEqual(response.status_code, 200)

    def test_get_submission_unauthenticated(self):
        view = SubmissionsDetail.as_view()

        request = self.factory.get(self.getApiUrl() + str(self.submission1.id) + '/')
        response = view(request, pk=self.submission1.id)

        self.assertEqual(response.status_code, 401)

    def test_update_submission(self):
        view = SubmissionsDetail.as_view()

        data = {
            'marks': 10
        }

        request = self.factory.patch(self.getApiUrl() + str(self.submission1.id) + '/', data)
        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request, pk=self.submission1.id)

        submission = Submission.objects.get(pk=self.submission1.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(submission.marks, 10)

    def test_update_submission_student(self):
        view = SubmissionsDetail.as_view()

        data = {
            'marks': 10
        }

        request = self.factory.patch(self.getApiUrl() + str(self.submission1.id) + '/', data)
        self.loginStudent(request)
        response = view(request, pk=self.submission1.id)

        self.assertEqual(response.status_code, 403)

    def test_update_submission_unauthenticated(self):
        view = SubmissionsDetail.as_view()

        data = {
            'marks': 10
        }

        request = self.factory.patch(self.getApiUrl() + str(self.submission1.id) + '/', data)
        response = view(request, pk=self.submission1.id)

        self.assertEqual(response.status_code, 401)

    def test_delete_submission(self):
        view = SubmissionsDetail.as_view()

        request = self.factory.delete(self.getApiUrl() + str(self.submission1.id) + '/')
        self.loginProfessor(request)
        response = view(request, pk=self.submission1.id)

        self.assertEqual(len(Submission.objects.all()), 1)
        self.assertEqual(response.status_code, 204)

    def test_delete_submission_student(self):
        view = SubmissionsDetail.as_view()

        request = self.factory.delete(self.getApiUrl() + str(self.submission1.id) + '/')
        self.loginStudent(request)
        response = view(request, pk=self.submission1.id)

        self.assertEqual(len(Submission.objects.all()), 2)
        self.assertEqual(response.status_code, 403)

    def test_delete_submission_unauthenticated(self):
        view = SubmissionsDetail.as_view()

        request = self.factory.delete(self.getApiUrl() + str(self.submission1.id) + '/')
        response = view(request, pk=self.submission1.id)

        self.assertEqual(len(Submission.objects.all()), 2)
        self.assertEqual(response.status_code, 401)
