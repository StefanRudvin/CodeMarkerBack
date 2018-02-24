import filecmp
import json
import os

from django.core import serializers

from codemarker.settings import MEDIA_ROOT
from app.docker_processor import start_docker_instance, generate_input
from app.models import Submission, Resource


def run_submission(submission_id, **kwargs):
    """

    :param submission_id:
    :return: data
    """
    # First get submission
    submission = Submission.objects.get(pk=submission_id)
    submission.status = "in_progress"
    submission.save()

    resource_language = Resource.objects.get(
        assessment_id=submission.assessment_id).language

    generate_input(submission, resource_language)
    start_docker_instance(submission)

    expected_output_dir = os.path.join(MEDIA_ROOT, str(
        submission.assessment_id), "expected_outputs")
    output_dir = os.path.join(MEDIA_ROOT, str(
        str(submission.assessment_id)), "submissions", str(submission_id), "outputs")

    # Test output
    if not filecmp.dircmp(expected_output_dir, output_dir).diff_files:
        submission.result = "pass"
        submission.marks = 100
        submission.info = "All tests cleared! Great job!"
    else:
        failed_output = ""
        for failed in filecmp.dircmp(expected_output_dir, output_dir).diff_files:
            file = open(os.path.join(output_dir, failed), "r")
            failed_output += file.read()
            file.close()

        submission.result = "fail"
        submission.marks = 0
        submission.info = failed_output

    count = 0
    total = 0.0
    for filename in os.listdir(output_dir):

        if filename.startswith("t_"):
            file = open(os.path.join(output_dir, filename), "r")
            total += float(file.read())
            count += 1
            file.close()

    submission.timeTaken = total / count

    submission.status = "complete"

    submission.save()

    # Produce JSON output
    data = serializers.serialize('json', [submission, ])
    struct = json.loads(data)
    data = json.dumps(struct[0])

    return data
