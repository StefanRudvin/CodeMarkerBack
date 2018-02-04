from codemarker.serializers import CourseSerializer, AssessmentSerializer, SubmissionSerializer
from codemarker.models import Course, Assessment, Submission, Resource, InputGenerator
from codemarker.SubmissionProcessor import processSubmission
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import generics
from Tutorial import settings
import os


def index(request):
    return HttpResponse("Hello world. You're at the codemarker index.")


@csrf_exempt
def submissions_upload(request, assessment_id):
    if request.method == 'POST' and request.FILES['submission']:

        submission_file = request.FILES['submission']
        submission = Submission(
            filename=submission_file.name,
            content_type="python",
            status="start",
            result="fail",
            marks=0,
            user_id=1,
            assessment_id=assessment_id,
            timeTaken=0)
        submission.save()

        os.makedirs(os.path.join(settings.MEDIA_ROOT,
                                 assessment_id, 'submissions', str(submission.id)), exist_ok=True)
        fs = FileSystemStorage(location=os.path.join(
            settings.MEDIA_ROOT, assessment_id, 'submissions', str(submission.id)))

        filename = fs.save(submission_file.name, submission_file)
        uploaded_file_url = fs.url(filename)

        return HttpResponse(submission.id)

@csrf_exempt
def assessments_upload(request, course_id):
    if request.method == 'POST' and request.FILES['resource']:

        assessment = Assessment(
            name=request.POST.get("name", ""),
            description=request.POST.get("description", ""),
            additional_help=request.POST.get("additional_help", ""),
            resource="",
            input_generator="",
            course=course_id,)
        assessment.save()

        resource_file = request.FILES['resource']

        resource = Resource(
            filename=resource_file.name,
            content_type="python",
            status="start",
            assessment=assessment.id)
        resource.save()

        os.makedirs(os.path.join(settings.MEDIA_ROOT,
                                 resource.id, 'resources', str(resource.id)), exist_ok=True)
        fs = FileSystemStorage(location=os.path.join(
            settings.MEDIA_ROOT, resource.id, 'resources', str(resource.id)))

        fs.save(resource_file.name, resource_file)

        if request.FILES['input_generator_file']:
            input_generator_file = request.FILES['input_generator_file']

            input_generator = InputGenerator(
                filename=input_generator_file.name,
                content_type="python",
                assessment=assessment.id)
            input_generator.save()

            os.makedirs(os.path.join(settings.MEDIA_ROOT,
                                     input_generator.id, 'input_generators', str(input_generator.id)), exist_ok=True)
            fs = FileSystemStorage(location=os.path.join(
                settings.MEDIA_ROOT, input_generator.id, 'input_generators', str(input_generator.id)))

            fs.save(input_generator_file.name, input_generator_file)

            assessment.input_generator = input_generator.id

        assessment.resource = resource.id

        assessment.save()

        return HttpResponse(assessment.id)


def submissionsProcess(request, submission_id):
    return HttpResponse(processSubmission(submission_id), content_type='text/plain')


class CoursesList(generics.ListCreateAPIView):
    """
        List all courses.
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CoursesDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single course.
        :rtype: Course
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class AssessmentsList(generics.ListCreateAPIView):
    """
        List all assessments.
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AssessmentsDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single Assessment.
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer


class SubmissionsList(generics.ListCreateAPIView):
    """
        List all submissions.
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubmissionsDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single submission.
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
