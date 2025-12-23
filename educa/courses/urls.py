from django.urls import path

from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.SubjectListView.as_view(), name='subject_list'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('subjects/<slug:subject>/', views.CourseListView.as_view(), name='course_list_by_subject'),
    path('courses/<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),

    path('manage/courses/', views.ManageCourseListView.as_view(), name='manage_course_list'),
    path('manage/courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('manage/courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('manage/courses/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),

    path('manage/courses/<int:pk>/modules/', views.CourseModuleUpdateView.as_view(), name='course_module_update'),
    path('manage/modules/<int:module_id>/contents/', views.ModuleContentListView.as_view(), name='module_content_list'),

    path('manage/modules/<int:module_id>/content/<model_name>/create/', views.ContentCreateUpdateView.as_view(), name='content_create'),
    path('manage/modules/<int:module_id>/content/<model_name>/<int:id>/', views.ContentCreateUpdateView.as_view(), name='content_update'),
    path('manage/content/<int:id>/delete/', views.ContentDeleteView.as_view(), name='content_delete'),
]
