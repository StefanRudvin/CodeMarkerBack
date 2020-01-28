"""
Module responsible for all Business Logic related to marking and assessing the solution.
Uses filecmp to compare desired outputs with actual outputs to assign specific marks.

@TeamAlpha 2018
CodeMarker
submission_processor.py
"""

import filecmp
import json
import logging
import os
from decimal import Decimal

from django.core import serializers

from app.docker_processor import generate_input, run_dynamic, run_static
from app.models import Assessment, Resource, Submission
from codemarker.settings import MEDIA_ROOT

LOGGER = logging.getLogger(__name__)


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

    expected_output_dir = os.path.join(
        MEDIA_ROOT, str(submission.assessment_id), "expected_outputs"
    )
    expected_static_output_dir = os.path.join(
        MEDIA_ROOT, str(submission.assessment_id), "expected_static_outputs"
    )
    output_dir = os.path.join(
        MEDIA_ROOT,
        str(str(submission.assessment_id)),
        "submissions",
        str(submission_id),
        "outputs",
    )
    static_output_dir = os.path.join(
        MEDIA_ROOT,
        str(str(submission.assessment_id)),
        "submissions",
        str(submission_id),
        "static_outputs",
    )
    print(assessment)

    if assessment.static_input:
        submission.info = submission.info + "\nRUNNING STATIC INPUT. \n"
        run_static(submission, assessment)
        test_outputs(
            expected_static_output_dir,
            static_output_dir,
            submission,
            assessment.max_time,
        )
    if assessment.dynamic_input:
        submission.info = submission.info + "\nRUNNING DYNAMIC INPUT. \n"
        resource_language = Resource.objects.get(
            assessment_id=submission.assessment_id
        ).language
        generate_input(submission, resource_language)
        run_dynamic(submission)
        test_outputs(expected_output_dir, output_dir, submission, assessment.max_time)

    # Produce JSON output
    data = serializers.serialize("json", [submission,])
    struct = json.loads(data)
    data = json.dumps(struct[0])

    return data


def test_outputs(expected_output_dir, output_dir, submission, max_time):
    """Method testing whether the output matches the expected output
    """
    if not filecmp.dircmp(expected_output_dir, output_dir).diff_files:
        submission.result = "pass"
        submission.marks = 100
        submission.info = submission.info + " All tests cleared!\n"
    else:
        LOGGER.error(filecmp.dircmp(expected_output_dir, output_dir).diff_files)
        failed_output = ""
        for failed in filecmp.dircmp(expected_output_dir, output_dir).diff_files:
            file = open(os.path.join(output_dir, failed), "r")
            failed_output += file.read()
            file.close()

        submission.result = "fail"
        submission.marks = 0
        submission.info = submission.info + failed_output

    total = []
    for filename in os.listdir(output_dir):
        if filename.startswith("t_"):
            file = open(os.path.join(output_dir, filename), "r")
            total.append(Decimal(file.read()))
            file.close()

    submission.timeTaken = round(max(total), 3)
    submission.status = "complete"

    if (max_time > 0 and submission.timeTaken > max_time):
        submission.marks = 0
        submission.info = (
            submission.info
            + f"\n Runtime of your program exceeded maximum allowance of {max_time}\n"
        )
        submission.result = "overtime"

    submission.save()
