from rest_framework.test import force_authenticate
from app.tests.CustomTestCase import CustomTestCase
from app.views import AssessmentsList, AssessmentsDetail
from app.models import Assessment


class TestAssessments(CustomTestCase):
    def test_get_assessments(self):
        view = AssessmentsList.as_view()

        request = self.factory.get('/api/assessments/')
        force_authenticate(request, user=self.student, token=self.student.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_assessments_student(self):
        view = AssessmentsList.as_view()

        request = self.factory.get('/api/assessments/')
        self.loginStudent(request)
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_assessments_unauthenticated(self):
        view = AssessmentsList.as_view()

        request = self.factory.get('/api/assessments/')
        response = view(request)

        self.assertEqual(response.status_code, 401)

    def test_create_assessments(self):
        view = AssessmentsList.as_view()

        with open('./demo/Python3/generator.py') as generator:
            with open('./demo/Python3/resource.py') as resource:
                data = self.createAssessmentData(resource, generator)

                request = self.factory.post('/api/assessments/', data)

                force_authenticate(request, user=self.professor, token=self.professor.auth_token)
                response = view(request)

                self.assertEqual(response.status_code, 201)
                self.assertEqual(len(Assessment.objects.all()), 3)

    def test_create_assessments_unauthenticated(self):
        view = AssessmentsList.as_view()

        request = self.factory.post('/api/assessments/')
        response = view(request)

        self.assertEqual(response.status_code, 401)

    def test_create_assessments_student(self):
        view = AssessmentsList.as_view()

        request = self.factory.post('/api/assessments/')
        force_authenticate(request, user=self.student, token=self.student.auth_token)
        response = view(request)

        self.assertEqual(response.status_code, 403)

    def test_get_assessment(self):
        view = AssessmentsDetail.as_view()

        request = self.factory.get('/api/assessments/' + str(self.assessment1.id) + '/')
        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request, pk=self.assessment1.id)

        self.assertEqual(response.status_code, 200)

    def test_get_assessment_student(self):
        view = AssessmentsDetail.as_view()

        request = self.factory.get('/api/assessments/' + str(self.assessment1.id) + '/')
        self.loginStudent(request)
        response = view(request, pk=self.assessment1.id)

        self.assertEqual(response.status_code, 403)

    def test_get_assessment_unauthenticated(self):
        view = AssessmentsDetail.as_view()

        request = self.factory.get('/api/assessments/' + str(self.assessment1.id) + '/')
        response = view(request, pk=self.assessment1.id)

        self.assertEqual(response.status_code, 401)

    def test_update_assessment(self):
        view = AssessmentsDetail.as_view()

        data = {
            'name': 'NewName'
        }

        request = self.factory.patch('/api/assessments/' + str(self.assessment1.id) + '/', data)
        force_authenticate(request, user=self.professor, token=self.professor.auth_token)
        response = view(request, pk=self.assessment1.id)

        assessment = Assessment.objects.get(pk=self.assessment1.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(assessment.name, 'NewName')

    def test_update_assessment_student(self):
        view = AssessmentsDetail.as_view()

        data = {
            'name': 'NewName'
        }

        request = self.factory.patch('/api/assessments/' + str(self.assessment1.id) + '/', data)
        self.loginStudent(request)
        response = view(request, pk=self.assessment1.id)

        self.assertEqual(response.status_code, 403)

    def test_update_assessment_unauthenticated(self):
        view = AssessmentsDetail.as_view()

        data = {
            'name': 'NewName'
        }

        request = self.factory.patch('/api/assessments/' + str(self.assessment1.id) + '/', data)
        response = view(request, pk=self.assessment1.id)

        self.assertEqual(response.status_code, 401)

    def test_delete_assessment(self):
        view = AssessmentsDetail.as_view()

        request = self.factory.delete('/api/assessments/' + str(self.assessment1.id) + '/')
        self.loginProfessor(request)
        response = view(request, pk=self.assessment1.id)

        self.assertEqual(len(Assessment.objects.all()), 1)
        self.assertEqual(response.status_code, 204)

    def test_delete_assessment_student(self):
        view = AssessmentsDetail.as_view()

        request = self.factory.delete('/api/assessments/' + str(self.assessment1.id) + '/')
        self.loginStudent(request)
        response = view(request, pk=self.assessment1.id)

        self.assertEqual(len(Assessment.objects.all()), 2)
        self.assertEqual(response.status_code, 403)

    def test_delete_assessment_unauthenticated(self):
        view = AssessmentsDetail.as_view()

        request = self.factory.delete('/api/assessments/' + str(self.assessment1.id) + '/')
        response = view(request, pk=self.assessment1.id)

        self.assertEqual(len(Assessment.objects.all()), 2)
        self.assertEqual(response.status_code, 401)
