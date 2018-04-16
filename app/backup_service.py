"""
Module containing methods for creating and restoring backups of the system

@TeamAlpha 2018
CodeMarker
backup_service.py
"""

import os
import shutil
import time
import zipfile

from django.core.files.storage import FileSystemStorage
from django.core.management import call_command
from rest_framework.response import Response


def create_backup():
    """Create backup zip and store it in the backups/ folder

    Returns:
        response -- description whether backup was successful
    """

    # Create timestamp for the file
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # Create a json file and open it, redirecting the output
    with open('uploads/sql.json', 'w') as sql_file:
        # Dump all data to the created json file
        call_command('dumpdata', exclude=['authtoken.Token'], natural_foreign=True, stdout=sql_file)

    # Create zip file containing the file system and backup in the backups folder
    os.makedirs('backups', exist_ok=True)
    shutil.make_archive(
        'backups/' + timestamp, 'zip', 'uploads')

    # Clean-up the solution and remove created helper files
    try:
        os.remove('uploads/sql.json')
    except OSError:
        pass

    # Return the response with the information whether it was successful or not.
    return Response("Backup has been created")


def restore_backup(request):
    """Provided a backup file, restore the file system from it

    Returns:
        request -- whether backup was successful or not.
    """

    # Very important, create a backup of the current system state first.
    create_backup()

    # Save uploaded archive containing backup
    zip_archive = request.FILES.get("backup")
    file_storage = FileSystemStorage(location='./')
    file_storage.save('backup.zip', zip_archive)

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

    # Return whether response was successful or not
    return Response("Backup has been restored successfully")
