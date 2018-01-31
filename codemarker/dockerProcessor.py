import docker
from Tutorial.settings import MEDIA_ROOT
import os


def startDockerInstance(submission):
    client = docker.from_env()

    container = client.containers.run("python",
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
                                      command="/bin/bash /mnt/vol2/run_python.sh %s %s %s" % (submission.filename, submission.assessment_id, submission.id))
