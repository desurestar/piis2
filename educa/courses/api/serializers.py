import logging

from rest_framework import serializers
from django.db.models import Count
from ..models import Content, Course, Module, Subject

logger = logging.getLogger(__name__)

class SubjectSerializer(serializers.ModelSerializer):
    total_courses = serializers.IntegerField(read_only=True)
    popular_courses = serializers.SerializerMethodField()

    def get_popular_courses(self, obj):
        courses = obj.courses.annotate(
            total_students=Count('students')
        ).order_by('-total_students')[:3]
        return [
            f'{c.title} ({c.total_students})' for c in courses
        ]

    class Meta:
        model = Subject
        fields = [
            'id',
            'title',
            'slug',
            'total_courses',
            'popular_courses',
        ]


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'subject',
            'title',
            'slug',
            'overview',
            'created',
            'owner',
            'modules',
        ]


class ItemRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if value is None:
            return None
        render = getattr(value, 'render', None)
        if callable(render):
            try:
                return render()
            except (AttributeError, TypeError, ValueError):
                # render() is expected on content items; fall back to a string
                # representation if it is missing or raises type/value errors from
                # invalid content or templates.
                logger.exception('Failed to render content item %s', value)
                return str(value)
        return str(value)


class ContentSerializer(serializers.ModelSerializer):
    item = ItemRelatedField(read_only=True)

    class Meta:
        model = Content
        fields = ['order', 'item']


class ModuleWithContentsSerializer(ModuleSerializer):
    contents = ContentSerializer(many=True, read_only=True)

    class Meta(ModuleSerializer.Meta):
        fields = ModuleSerializer.Meta.fields + ['contents']


class CourseWithContentsSerializer(CourseSerializer):
    modules = ModuleWithContentsSerializer(many=True, read_only=True)

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields
