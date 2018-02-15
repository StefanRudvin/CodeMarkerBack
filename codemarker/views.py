from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.views import APIView

from codemarker.serializers import CourseSerializer, AssessmentSerializer, SubmissionSerializer, UserSerializer
from codemarker.models import Course, Assessment, Submission, Resource, InputGenerator
from codemarker.SubmissionProcessor import processSubmission
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import generics
from django.conf import settings
import os


def index(request):
    return HttpResponse("Hello world. You're at the codemarker index.")


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, pk=None):
        if pk == 'i':
            return HttpResponse(UserSerializer(request.user,
                                               context={'request': request}).data)
        return super(UserViewSet, self).retrieve(request, pk)


@csrf_exempt
def submissions_upload(request, assessment_id: int) -> HttpResponse:
    """
    Upload a new submission linked to an assessment

    :param request:
    :type request
    :param assessment_id:
    :return: HttpResponse
    """

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


class GetUser(APIView):

    def get(self, request, format=None):
        #user = User.objects.get(username=request.user)


        #content = {
        #    'user': request.user.username,  # `django.contrib.auth.User` instance.
        #    'auth': request.auth,  # None
        #}

        user = UserSerializer(request.user)

        return JsonResponse(user, safe=False)


@csrf_exempt
def assessments_upload(request, course_id: int) -> HttpResponse:
    """
    Create a new assessment with resource and input_generator files

    :return: HttpResponse
    :rtype: HttpResponse
    :param request:
    :type request:
    :param course_id:
    """

    if request.method == 'POST' and request.FILES['resource']:

        course = Course.objects.get(pk=course_id)

        assessment = Assessment(
            name=request.POST.get("name", ""),
            description=request.POST.get("description", ""),
            additional_help=request.POST.get("additional_help", ""),
            course=course)
        assessment.save()

        resource_file = request.FILES['resource']

        resource = Resource(
            filename=resource_file.name,
            content_type="python",
            status="start",
            assessment=assessment)
        resource.save()

        os.makedirs(os.path.join(settings.MEDIA_ROOT,
                                 str(assessment.id), 'resources', str(resource.id)), exist_ok=True)
        fs = FileSystemStorage(location=os.path.join(
            settings.MEDIA_ROOT, str(assessment.id), 'resources', str(resource.id)))

        fs.save(resource_file.name, resource_file)

        if request.FILES['input_generator']:
            input_generator_file = request.FILES['input_generator']

            input_generator = InputGenerator(
                filename=input_generator_file.name,
                content_type="python",
                assessment=assessment)
            input_generator.save()

            os.makedirs(os.path.join(settings.MEDIA_ROOT,
                                     str(assessment.id), 'input_generators', str(input_generator.id)), exist_ok=True)
            fs = FileSystemStorage(location=os.path.join(
                settings.MEDIA_ROOT, str(assessment.id), 'input_generators', str(input_generator.id)))

            fs.save(input_generator_file.name, input_generator_file)

            assessment.input_generator = input_generator

        assessment.resource = resource

        assessment.save()

        return HttpResponse(assessment.id)


def process_submission(request, submission_id: int) -> HttpResponse:
    """
    Process a submission with Docker and processSubmission.py

    :param request:
    :param submission_id:
    :return: HttpResponse
    """

    return HttpResponse(processSubmission(submission_id), content_type='text/plain')


class CoursesList(generics.ListCreateAPIView):
    """
        List all courses using RestFramework.
        :rtype: CourseSerializer
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CoursesDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single course using RestFramework.
        :rtype: Course
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class AssessmentsList(generics.ListCreateAPIView):
    """
        List all assessments using RestFramework.
        :rtype: AssessmentSerializer
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AssessmentsDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single Assessment.
        :rtype: AssessmentSerializer
    """

    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer


class SubmissionsList(generics.ListCreateAPIView):
    """
        List all submissions.
        :rtype: SubmissionSerializer
    """

    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubmissionsDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single submission.
        :rtype: SubmissionSerializer
    """

    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
