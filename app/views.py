import logging
import os
import shutil
import time
import zipfile

from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.management import call_command
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden, HttpResponseServerError)
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from app.factory import assessment_creator, course_creator, submission_creator
from app.models import Assessment, Course, Submission
from app.serializers import (AssessmentSerializer, CourseSerializer,
                             CoursesUsersSerializer, SubmissionSerializer,
                             UserSerializer)
from app.submission_processor import run_submission

# Get an instance of a logger
logger = logging.getLogger(__name__)


class CustomObtainAuthToken(ObtainAuthToken):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(
            request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({
            'token': token.key,
            'id': token.user_id,
            'username': token.user.username,
            'superuser': token.user.is_superuser,
            'staff': token.user.is_staff,
        })


def index(request):
    return HttpResponse("Hello world. You're at the codemarker index.")


def create_backup(request=None):
    """
    Create back up of the current system,
    that's including SQL (formatted as JSON) and file system
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = 'backups/'+timestamp+'.zip'

    with open('uploads/sql.json', 'w') as f:
        call_command('dumpdata', stdout=f)
    os.makedirs('backups', exist_ok=True)
    shutil.make_archive(
        'backups/'+timestamp, 'zip', 'uploads')
    try:
        os.remove('uploads/sql.json')
    except OSError:
        pass

    # mimetype is replaced by content_type for django 1.7
    response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(
        timestamp+'.zip')
    response['X-Sendfile'] = smart_str(path)

    return response


@csrf_exempt
def restore_backup(request):
    """
    Restore uploaded zip file containing backed up system
    """

    # Very important, create a backup of the current system state first.
    create_backup()

    # Save uploaded archive containing backup
    zip_archive = request.FILES.get("backup")
    fs = FileSystemStorage(location='./')
    fs.save('backup.zip', zip_archive)

    # Remove current file system (safe, as we did a backup before)
    shutil.rmtree('uploads/')
    os.makedirs('uploads', exist_ok=True)

    # Extract contents of the zipfile containing backup
    zip_ref = zipfile.ZipFile('backup.zip', 'r')
    zip_ref.extractall('uploads')
    zip_ref.close()

    # Load fixtures into DB
    call_command('loaddata', 'uploads/sql.json')

    # Clean up uploaded files
    os.remove('uploads/sql.json')
    os.remove('backup.zip')
    return HttpResponse()


# // TODO:  Add permissions
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, pk=None):
        if pk == 'i':
            return HttpResponse(UserSerializer(request.user,
                                               context={'request': request}).data)
        return super(UserViewSet, self).retrieve(request, pk)


def process_submission(request, submission_id) -> HttpResponse:
    """
    Process a submission with Docker and process_submission.py

    :param request:
    :param submission_id:
    :return: HttpResponse
    """

    try:
        result = run_submission(submission_id)
        return HttpResponse(result, content_type='text/plain')
    except Exception as e:
        logger.error(e)
        return HttpResponseServerError("An error occurred in processing your submission."
                                       "If this persists please contact the administrator.")


class CoursesList(generics.ListCreateAPIView):
    """
        List all courses using RestFramework.
        :rtype: CourseSerializer
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    """
        Concrete view for listing a queryset or creating a model instance.
    """

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Course.objects.all()

        if user.is_staff:
            return Course.objects.filter(professor=user)

        return Course.objects.filter(students=user)

    def post(self, request, *args, **kwargs):

        if not self.request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to create assessments")
        return self.create(request, *args, **kwargs)


class CoursesDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single course using RestFramework.
        :rtype: Course
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def put(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to update courses")
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to update courses")
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to destroy courses")
        return self.destroy(request, *args, **kwargs)


class CoursesUsersDestroy(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CoursesUsersSerializer

    def post(self, request, *args, **kwargs):
        course_id = self.request.POST.get("course_id", "")

        user_id = self.request.POST.get("user_id", "")

        course = Course.objects.get(pk=course_id)

        user = User.objects.get(pk=user_id)

        course.students.remove(user)

        return Response('Success')


class CoursesUsersAdd(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CoursesUsersSerializer

    def post(self, request, *args, **kwargs):
        course_id = self.request.POST.get("course_id", "")

        user_id = self.request.POST.get("user_id", "")

        course = Course.objects.get(pk=course_id)

        user = User.objects.get(pk=user_id)

        if user in course.students.all():
            return HttpResponseBadRequest('The user is already enrolled to this course!')
        else:
            return Response(course.students.add(user))


class AssessmentsList(generics.ListCreateAPIView):
    """
        List all assessments and create using RestFramework.
        :rtype: AssessmentSerializer
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

    def post(self, serializer):
        return assessment_creator(self, serializer)


class AssessmentsDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single Assessment.
        :rtype: AssessmentSerializer
    """

    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

    def perform_update(self, serializer):

        if not self.request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to update assessments")

        serializer.update()

    def perform_destroy(self, serializer):
        if not self.request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to destroy assessments")

        serializer.destroy()


class UsersList(generics.ListCreateAPIView):
    """
        List all users and create using RestFramework.
        :rtype: UserSerializer
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UsersDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single user.
        :rtype: SubmissionSerializer
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['pk']

        user = User.objects.get(pk=user_id)
        userJson = UserSerializer(user).data

        courses = Course.objects.filter(students=user)
        coursesJson = CourseSerializer(courses, many=True).data

        submissions = Submission.objects.filter(user=user)
        submissionsJson = SubmissionSerializer(submissions, many=True).data

        userJson['submissions'] = submissionsJson
        userJson['courses'] = coursesJson

        return Response(userJson)

    def put(self, request, *args, **kwargs):
        username = self.request.POST.get("username", "")

        user_id = self.request.POST.get("id", "")

        is_staff = self.request.POST.get("is_staff", "")

        email = self.request.POST.get("email", "")

        user = User.objects.get(pk=user_id)
        user.username = username
        user.email = email
        user.is_staff = is_staff == 'true'
        user.save()

        return Response(200)


class SubmissionsList(generics.ListCreateAPIView):
    """
        List all submissions.
        :rtype: SubmissionSerializer
    """

    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def post(self, serializer):
        return submission_creator(self, serializer)


class SubmissionsDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single submission.
        :rtype: SubmissionSerializer
    """

    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def post(self, serializer):

        if not self.request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to update submissions")

        serializer.update()

    def perform_destroy(self, serializer):
        if not self.request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to destroy submissions")

        serializer.destroy()
