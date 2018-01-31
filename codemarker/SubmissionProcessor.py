from codemarker.models import Submission
from subprocess import Popen, PIPE, STDOUT
from django.core import serializers
import random
import time
import json
from codemarker.dockerProcessor import startDockerInstance
from Tutorial.settings import MEDIA_ROOT
import os
import filecmp


def processSubmission(submission_id):
    # First get submission
    submission = Submission.objects.get(pk=submission_id)
    submission.status = "in_progress"
    submission.save()

    startDockerInstance(submission)

    expected_output_dir = os.path.join(MEDIA_ROOT, str(
        submission.assessment_id), "expected_outputs")
    output_dir = os.path.join(MEDIA_ROOT, str(
        str(submission.assessment_id)), "submissions", str(submission_id), "outputs")

    # Test output
    if not filecmp.dircmp(expected_output_dir, output_dir).diff_files:
        submission.result = "pass"
        submission.marks = 100
    else:
        submission.result = "fail"
        submission.marks = 0

    submission.timeTaken = 0.005

    submission.status = "complete"

    submission.save()

    # Produce JSON output
    data = serializers.serialize('json', [submission, ])
    struct = json.loads(data)
    data = json.dumps(struct[0])

    return data
