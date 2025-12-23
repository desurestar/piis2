from rest_framework import decorators, generics, viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Course, Subject
from .serializers import (
    CourseSerializer,
    CourseWithContentsSerializer,
    SubjectSerializer,
)

from django.db.models import Count
from .pagination import StandardPagination


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.annotate(
        total_courses=Count('courses')
    )
    serializer_class = SubjectSerializer
    pagination_class = StandardPagination

class CourseEnrollView(generics.GenericAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course = self.get_object()
        _, created = course.students.through.objects.get_or_create(
            course=course,
            user=request.user,
        )
        return Response({'enrolled': True, 'new_enrollment': created})



class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @decorators.action(detail=True, methods=['get'])
    def contents(self, request, *args, **kwargs):
        course = self.get_object()
        serializer = CourseWithContentsSerializer(course)
        return Response(serializer.data)
