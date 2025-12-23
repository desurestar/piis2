from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .models import Course, Subject


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
)
class CourseAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.subject = Subject.objects.create(title='Math', slug='math')
        self.owner = User.objects.create_user(username='owner', password='pass')
        self.course = Course.objects.create(
            owner=self.owner,
            subject=self.subject,
            title='Course',
            slug='course',
            overview='Overview',
        )

    def test_api_root_lists_registered_viewsets(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('courses', response.data)
        self.assertIn('subjects', response.data)

    def test_course_enroll_view_requires_authentication(self):
        enroll_url = f'/api/courses/{self.course.id}/enroll/'
        response = self.client.post(enroll_url)
        self.assertEqual(response.status_code, 401)

        student = User.objects.create_user(username='student', password='pass')
        self.client.force_authenticate(user=student)
        authed_response = self.client.post(enroll_url)
        self.assertEqual(authed_response.status_code, 200)
        self.assertTrue(authed_response.data.get('enrolled'))
        self.assertTrue(self.course.students.filter(id=student.id).exists())
