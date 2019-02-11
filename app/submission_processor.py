"""
Module responsible for all Business Logic related to marking and assessing the solution.
Uses filecmp to compare desired outputs with actual outputs to assign specific marks.

@TeamAlpha 2018
CodeMarker
submission_processor.py
"""

import filecmp
import json
import os
import logging
from django.core import serializers

from app.docker_processor import generate_input, run_dynamic, run_static
from app.models import Assessment, Resource, Submission
from codemarker.settings import MEDIA_ROOT

logger = logging.getLogger(__name__)

def run_submission(submission_id):
    """Run submission in a docker container

    Arguments:
        submission_id - ID of the submission that we're running

    Returns:
        JSON dump, whether it was successful or not
    """

    # First get submission
    submission = Submission.objects.get(pk=submission_id)
    submission.status = "in_progress"
    submission.save()
    assessment = Assessment.objects.get(id=submission.assessment_id)

    expected_output_dir = os.path.join(MEDIA_ROOT, str(
        submission.assessment_id), "expected_outputs")
    expected_static_output_dir = os.path.join(MEDIA_ROOT, str(
        submission.assessment_id), "expected_static_outputs")
    output_dir = os.path.join(MEDIA_ROOT, str(
        str(submission.assessment_id)), "submissions", str(submission_id), "outputs")
    static_output_dir = os.path.join(MEDIA_ROOT, str(
        str(submission.assessment_id)), "submissions", str(submission_id), "static_outputs")

    if assessment.static_input:
        submission.info=submission.info+"RUNNING STATIC INPUT. \n"
        run_static(submission, assessment)
        test_outputs(expected_static_output_dir, static_output_dir, submission)
    if assessment.dynamic_input:
        submission.info=submission.info+"RUNNING DYNAMIC INPUT. \n"
        resource_language = Resource.objects.get(
            assessment_id=submission.assessment_id).language
        generate_input(submission, resource_language)
        run_dynamic(submission)
        test_outputs(expected_output_dir, output_dir, submission)

    # Produce JSON output
    data = serializers.serialize('json', [submission, ])
    struct = json.loads(data)
    data = json.dumps(struct[0])

    return data


def test_outputs(expected_output_dir, output_dir, submission):
    """Method testing whether the output matches the expected output
    """
    logger.error(expected_output_dir)
    logger.error(output_dir)
    if not filecmp.dircmp(expected_output_dir, output_dir).diff_files:
        submission.result = "pass"
        submission.marks = 100
        submission.info = submission.info+" All tests cleared! Great job! \n"
    else:
        logger.error(filecmp.dircmp(expected_output_dir, output_dir).diff_files)
        failed_output = ""
        for failed in filecmp.dircmp(expected_output_dir, output_dir).diff_files:
            file = open(os.path.join(output_dir, failed), "r")
            failed_output += file.read()
            file.close()

        submission.result = "fail"
        submission.marks = 0
        submission.info = submission.info+failed_output

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
