from rest_framework import serializers

from codemarker.models import Course


class CourseSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Course
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')
        extra_kwargs = {
            'url': {
                'view_name': 'course:course-detail',
            }
        }