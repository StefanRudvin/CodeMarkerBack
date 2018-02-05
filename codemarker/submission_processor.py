import filecmp
import json
import os

from django.core import serializers

from Tutorial.settings import MEDIA_ROOT
from codemarker.docker_processor import start_docker_instance, generate_input
from codemarker.models import Submission


def run_submission(submission_id, **kwargs):
    """

    :param submission_id:
    :return: data
    """
    # First get submission
    submission = Submission.objects.get(pk=submission_id)
    submission.status = "in_progress"
    submission.save()

    generate_input(submission)
    start_docker_instance(submission)

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
