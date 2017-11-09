from rest_framework import serializers

from codemarker.models import Course, Assessment


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ('id', 'name', 'description', 'created_at', 'updated_at', 'assessments')
        extra_kwargs = {
            'url': {
                'view_name': 'course:course-detail',
            }
        }


class AssessmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assessment
        fields = ('id', 'name', 'created_at', 'updated_at', 'course_id', 'resource_id')
        extra_kwargs = {
            'url': {
                'view_name': 'assessment:assessment-detail',
            }
        }