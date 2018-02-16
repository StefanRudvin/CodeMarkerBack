from rest_framework import serializers
from django.contrib.auth.models import User

from django.conf import settings
from codemarker.models import Course, Assessment, Submission


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    email = serializers.EmailField()
    username = serializers.CharField(max_length=100)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
        extra_kwargs = {
            'url': {
                'view_name': 'submission:submissions-detail',
            }
        }


class AssessmentSerializer(serializers.ModelSerializer):
    submissions = SubmissionSerializer(many=True, read_only=True)

    def create(self, validated_data):
        del validated_data['user']

        assessment = Assessment(**validated_data)
        assessment.save()
        return Assessment

    class Meta:
        model = Assessment
        fields = '__all__'
        extra_kwargs = {
            'url': {
                'view_name': 'assessment:assessments-detail',
            }
        }


class CourseSerializer(serializers.ModelSerializer):
    assessments = AssessmentSerializer(many=True, read_only=True)

    def create(self, validated_data):
        del validated_data['user']

        course = Course(**validated_data)

        course.user = User.objects.get(pk=1)
        course.save()
        return course

    class Meta:
        model = Course
        fields = ('id', 'name', 'description', 'created_at', 'updated_at', 'assessments', 'user_id')
        extra_kwargs = {
            'url': {
                'view_name': 'course:courses-detail',
            }
        }
