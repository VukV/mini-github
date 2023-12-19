from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from apps.history.models import History
from apps.repository.models import Repository


class HomeViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_home_view_status_code(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


class DashboardViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', public=True, owner=cls.user)

    def test_dashboard_view_status_code(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_view_uses_correct_template(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'home/dashboard.html')

    def test_dashboard_view_context_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertTrue('repositories' in response.context)
        self.assertTrue('recent_activity' in response.context)
        self.assertEqual(list(response.context['repositories']), [self.repository])
