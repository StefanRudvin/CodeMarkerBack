from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError

from app.serializers import CourseSerializer, AssessmentSerializer, SubmissionSerializer, UserSerializer, \
    CoursesUsersSerializer
from app.models import Course, Assessment, Submission
from app.submission_processor import run_submission
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import generics
from rest_framework import viewsets

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from app.factory import submission_creator
from app.factory import assessment_creator
from app.factory import course_creator


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
        print(e)
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

    def perform_update(self, serializer):

        if not self.request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to update submissions")

        serializer.update()

    def perform_destroy(self, serializer):
        if not self.request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to destroy submissions")

        serializer.destroy()
