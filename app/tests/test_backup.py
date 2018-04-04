from app.tests.CustomTestCase import CustomTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from app.views import CreateBackup, RestoreBackup
import glob
import os
from django.core.management import call_command


class TestBackups(CustomTestCase):
    def test_create_backup(self):
        view = CreateBackup.as_view()

        request = self.factory.post('api/create_backup/')
        self.loginProfessor(request)

        response = view(request)

        self.assertEqual(response.status_code, 200)

        list_of_files = glob.glob('backups/*.zip')
        latest_file = max(list_of_files, key=os.path.getctime)

        # Delete backup after its created
        os.remove(latest_file)

    def test_create_backup_student(self):
        view = CreateBackup.as_view()

        request = self.factory.post('api/create_backup/')
        self.loginStudent(request)
        response = view(request)

        self.assertEqual(response.status_code, 403)

    def test_create_backup_unauthorized(self):
        view = CreateBackup.as_view()

        request = self.factory.post('api/create_backup/')
        response = view(request)

        self.assertEqual(response.status_code, 401)

    # def test_restore_backup(self):
    #     view = RestoreBackup.as_view()

    #     with open('backups/' + os.listdir('backups')[0], 'rb') as fp:
    #         print(os.listdir('backups')[0])
    #         request = self.factory.post('api/create_backup/', {'backup': fp})
    #         self.loginProfessor(request)
    #         response = view(request)

    #         self.assertEqual(response.status_code, 200)

    def test_create_restore_student(self):
        view = RestoreBackup.as_view()

        request = self.factory.post('api/restore_backup/')
        self.loginStudent(request)
        response = view(request)

        self.assertEqual(response.status_code, 403)

    def test_create_restore_unauthorized(self):
        view = RestoreBackup.as_view()

        request = self.factory.post('api/restore_backup/')
        response = view(request)

        self.assertEqual(response.status_code, 401)
