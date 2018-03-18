import os
import shutil
import time
import zipfile

from django.core.files.storage import FileSystemStorage
from django.core.management import call_command
from django.http import HttpResponse
from django.utils.encoding import smart_str

import zipfile
from django.core.mail import EmailMessage
from rest_framework.response import Response


def create_backup(request):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = 'backups/' + timestamp + '.zip'

    with open('uploads/sql.json', 'w') as f:
        call_command('dumpdata', stdout=f)
    os.makedirs('backups', exist_ok=True)
    shutil.make_archive(
        'backups/' + timestamp, 'zip', 'uploads')
    try:
        os.remove('uploads/sql.json')
    except OSError:
        pass

    email = EmailMessage(
        'CodeMarker Backup',
        'You can find created backup in the attachments',
        's06kd7@abdn.ac.uk',
        ['kdryja@gmail.com'],
    )
    email.attach_file(path)
    email.send()

    return Response("Backup has been send to your email")


def restore_backup(request):
    # Very important, create a backup of the current system state first.
    create_backup(request)

    # Save uploaded archive containing backup
    zip_archive = request.FILES.get("backup")
    fs = FileSystemStorage(location='./')
    fs.save('backup.zip', zip_archive)

    # Remove current file system (safe, as we did a backup before)
    shutil.rmtree('uploads/')
    os.makedirs('uploads', exist_ok=True)

    # Extract contents of the zipfile containing backup
    zip_ref = zipfile.ZipFile('backup.zip', 'r')
    zip_ref.extractall('uploads')
    zip_ref.close()

    # Load fixtures into DB
    call_command('loaddata', 'uploads/sql.json')

    # Clean up uploaded files
    os.remove('uploads/sql.json')
    os.remove('backup.zip')
    return HttpResponse()
