import docker
from Tutorial.settings import MEDIA_ROOT
import os


def start_docker_instance(submission):
    client = docker.from_env()

    client.containers.run("python",
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
                          command=f"/bin/bash /mnt/vol2/run_python.sh {submission.filename} {submission.assessment_id} {submission.id}")


def generate_input(submission):
    client = docker.from_env()

    client.containers.run("python",
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
                          command=f"/bin/bash /mnt/vol2/generate_python.sh {submission.assessment_id}")
