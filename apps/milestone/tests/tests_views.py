from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.datetime_safe import date
from apps.milestone.models import Milestone
from apps.repository.models import Repository


class MilestonesFromRepositoryViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user_without_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.milestone = Milestone.objects.create(
            name='Milestone 1',
            description='First Milestone',
            date_due=date.today(),
            repository=cls.repository
        )

    def test_view_milestones_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.get(reverse('repository_milestones', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/milestones/repository_milestones.html')
        self.assertEqual(list(response.context['milestones']), [self.milestone])

    def test_view_milestones_without_access(self):
        self.client.login(username='user_without_access', password='testpass123')
        response = self.client.get(reverse('repository_milestones', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_view_milestones_unauthenticated(self):
        response = self.client.get(reverse('repository_milestones', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 302)


class AddMilestoneViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)

    def test_add_milestone_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        milestone_count_before = Milestone.objects.count()
        response = self.client.post(reverse('add_milestone', args=[self.repository.id]), {
            'name': 'Milestone 1',
            'description': 'Description of Milestone 1',
            'date_due': date.today().isoformat()
        })
        milestone_count_after = Milestone.objects.count()
        self.assertEqual(milestone_count_after, milestone_count_before + 1)
        self.assertRedirects(response, reverse('repository_milestones', args=[self.repository.id]))

    def test_add_milestone_without_access(self):
        other_user = User.objects.create_user(username='other_user', password='testpass123')
        self.client.login(username='other_user', password='testpass123')
        response = self.client.post(reverse('add_milestone', args=[self.repository.id]), {
            'name': 'Milestone 2',
            'description': 'Description of Milestone 2',
            'date_due': date.today().isoformat()
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_add_milestone_invalid_form(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('add_milestone', args=[self.repository.id]), {
            'name': '',
            'description': 'Description without a name',
            'date_due': 'invalid-date-format'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.', status_code=200)

    def test_add_milestone_unauthenticated_user(self):
        response = self.client.get(reverse('add_milestone', args=[self.repository.id]))
        self.assertEqual(response.status_code, 302)
