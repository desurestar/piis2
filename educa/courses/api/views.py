from rest_framework import decorators, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Course, Subject
from .serializers import (
    CourseSerializer,
    CourseWithContentsSerializer,
    SubjectSerializer,
)
from .permissions import IsEnrolled

from django.db.models import Count
from .pagination import StandardPagination


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.annotate(
        total_courses=Count('courses')
    )
    serializer_class = SubjectSerializer
    pagination_class = StandardPagination

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.prefetch_related('modules')
    serializer_class = CourseSerializer

    @decorators.action(
        detail=True,
        methods=['post'],
        authentication_classes=[BasicAuthentication],
        permission_classes=[IsAuthenticated],
    )
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled': True})

    @decorators.action(
        detail=True,
        methods=['get'],
        serializer_class=CourseWithContentsSerializer,
        authentication_classes=[BasicAuthentication],
        permission_classes=[IsAuthenticated, IsEnrolled],
    )
    def contents(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
