import logging

from django.contrib.auth.models import User
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden, HttpResponseServerError)
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response

from app.backup_service import create_backup, restore_backup
from app.factory import assessment_creator, import_users, submission_creator
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


class GetCurrentUserData(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=request.user.id)
        userJson = UserSerializer(user).data

        return Response(userJson)


class CreateBackup(generics.CreateAPIView):
    """
    Create back up of the current system,
    that's including SQL (formatted as JSON) and file system
    """

    def post(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return HttpResponseForbidden('You are not allowed to complete this action.')
        return create_backup()


class RestoreBackup(generics.CreateAPIView):
    """
    Create back up of the current system,
    that's including SQL (formatted as JSON) and file system
    """

    def post(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return HttpResponseForbidden('You are not allowed to complete this action.')
        return restore_backup(request)


class ImportUsers(generics.CreateAPIView):
    """
    Endpoint for importing new users from CSV file
    """

    def post(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return HttpResponseForbidden('You are not allowed to complete this action.')
        return import_users(request)


# TODO:  Add permissions
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissions,)
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

    permission_classes = (DjangoModelPermissions,)

    """
        Concrete view for listing a queryset or creating a model instance.
    """

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return Course.objects.all()

        # TODO: Find a way a attach a teacher to a course
        # if user.is_staff:
        #     return Course.objects.filter(professor=user)

        return Course.objects.filter(students=user)


class CoursesDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single course using RestFramework.
        :rtype: Course
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    permission_classes = (DjangoModelPermissions,)

    def get(self, request, *args, **kwargs):
        course_id = self.kwargs['pk']
        course = Course.objects.get(id=course_id)

        if request.user not in course.students.all() and not (request.user.is_staff or request.user.is_superuser):
            return HttpResponseForbidden('You are not allowed to access this resource.')

        return self.retrieve(request, *args, **kwargs)


class CoursesUsersDestroy(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CoursesUsersSerializer

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm('app.change_courses_users'):
            return HttpResponseForbidden("You are not allowed remove students from courses")

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

        if not request.user.has_perm('app.change_courses_users'):
            return HttpResponseForbidden("You are not allowed remove students from courses")

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

    permission_classes = (DjangoModelPermissions,)

    def post(self, serializer):
        return assessment_creator(self, serializer)


class AssessmentsDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single Assessment.
        :rtype: AssessmentSerializer
    """

    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

    permission_classes = (DjangoModelPermissions,)

    def get(self, request, *args, **kwargs):
        assessment_id = self.kwargs['pk']

        assessment = Assessment.objects.get(id=assessment_id)

        course = assessment.course

        if request.user not in course.students.all() and not (request.user.is_staff or request.user.is_superuser):
            return HttpResponseForbidden('You are not allowed to access this resource.')

        return self.retrieve(request, *args, **kwargs)


class UsersList(generics.ListCreateAPIView):
    """
        List all users and create using RestFramework.
        :rtype: UserSerializer
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    permission_classes = (DjangoModelPermissions,)


class UsersDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single user.
        :rtype: SubmissionSerializer
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    permission_classes = (DjangoModelPermissions,)

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['pk']

        if (int(user_id) != int(request.user.id)) and not request.user.is_staff:
            return HttpResponseForbidden('You are not allowed to access this resource.')

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

    permission_classes = (DjangoModelPermissions,)

    def post(self, serializer):
        return submission_creator(self, serializer)

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Submission.objects.all()

        # if user.is_staff:
        #     return Submission.objects.filter(professor=user)

        return Course.objects.filter(students=user)


class SubmissionsDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get a single submission.
        :rtype: SubmissionSerializer
    """

    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    permission_classes = (DjangoModelPermissions,)

    def get(self, request, *args, **kwargs):
        submission_id = self.kwargs['pk']

        submission = Submission.objects.get(id=submission_id)

        if (int(submission.user.id) != int(request.user.id)) and not (
                request.user.is_staff or request.user.is_superuser):
            return HttpResponseForbidden('You are not allowed to access this resource.')
        return self.retrieve(request, *args, **kwargs)
