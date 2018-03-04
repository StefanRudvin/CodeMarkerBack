import docker
from codemarker.settings import MEDIA_ROOT
import os


def run_dynamic(submission):
    """
    Run submitted code in docker container against generated input

    :param submission:
    """
    client = docker.from_env()

    client.containers.run("kdryja96/codemarker",
                          volumes={
                              MEDIA_ROOT:
                                  {
                                      'bind': '/mnt/vol1',
                                      'mode': 'rw'
                                  },
                              os.path.join(MEDIA_ROOT, '..', 'scripts'):
                                  {
                                      'bind': '/mnt/vol2',
                                      'mode': 'rw'
                              }
                          },
                          command=f"/bin/bash /mnt/vol2/run_dynamic.sh {submission.filename} {submission.assessment_id} {submission.id} {submission.language}")


def run_static(submission, assessment):
    """
    Run submitted code in docker container against provided static input

    :param submission:
    """
    client = docker.from_env()

    client.containers.run("kdryja96/codemarker",
                          volumes={
                              MEDIA_ROOT:
                                  {
                                      'bind': '/mnt/vol1',
                                      'mode': 'rw'
                                  },
                              os.path.join(MEDIA_ROOT, '..', 'scripts'):
                                  {
                                      'bind': '/mnt/vol2',
                                      'mode': 'rw'
                              }
                          },
                          command=f"/bin/bash /mnt/vol2/run_static.sh {submission.filename} {submission.assessment_id} {submission.id} {assessment.num_of_static}")


def generate_input(submission, resource_language):
    """
    Generate input for the dynamic run of the program

    :param submission:
    """
    client = docker.from_env()
    client.containers.run("kdryja96/codemarker",
                          volumes={
                              MEDIA_ROOT:
                                  {
                                      'bind': '/mnt/vol1',
                                      'mode': 'rw'
                                  },
                              os.path.join(MEDIA_ROOT, '..', 'scripts'):
                                  {
                                      'bind': '/mnt/vol2',
                                      'mode': 'rw'
                              }
                          },
                          command=f"/bin/bash /mnt/vol2/generate.sh {submission.assessment_id} {resource_language}")
