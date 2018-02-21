import docker
from Tutorial.settings import MEDIA_ROOT
import os


def start_docker_instance(submission):
    """
    Start docker instance and evaluate the submitted code

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
                                      'mode': 'ro'
                                  }
                          },
                          command=f"/bin/bash /mnt/vol2/run.sh {submission.filename} {submission.assessment_id} {submission.id} {submission.language}")


def generate_input(submission, resource_language):
    """

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
                                      'mode': 'ro'
                                  }
                          },
                          command=f"/bin/bash /mnt/vol2/generate.sh {submission.assessment_id} {resource_language}")
