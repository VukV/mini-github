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


class EditMilestoneViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.milestone = Milestone.objects.create(
            name='Initial Milestone',
            description='Initial Description',
            date_due=date.today(),
            repository=cls.repository
        )

    def test_edit_milestone_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('edit_milestone', args=[self.repository.id, self.milestone.id]), {
            'name': 'Updated Milestone',
            'description': 'Updated Description',
            'date_due': date.today().isoformat()
        })
        self.milestone.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.milestone.name, 'Updated Milestone')
        self.assertEqual(self.milestone.description, 'Updated Description')
        self.assertRedirects(response, reverse('repository_milestones', args=[self.repository.id]))

    def test_edit_milestone_without_access(self):
        other_user = User.objects.create_user(username='other_user', password='testpass123')
        self.client.login(username='other_user', password='testpass123')
        response = self.client.post(reverse('edit_milestone', args=[self.repository.id, self.milestone.id]), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_edit_milestone_invalid_form(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('edit_milestone', args=[self.repository.id, self.milestone.id]), {
            'name': '',
            'description': 'Updated Description',
            'date_due': date.today().isoformat()
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('This field is required.', response.content.decode())

    def test_edit_milestone_unauthenticated_user(self):
        response = self.client.get(reverse('edit_milestone', args=[self.repository.id, self.milestone.id]))
        self.assertEqual(response.status_code, 302)


class CloseMilestoneViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user_without_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.open_milestone = Milestone.objects.create(
            name='Open Milestone',
            description='A milestone that is open',
            date_due=date.today(),
            closed=False,
            repository=cls.repository
        )
        cls.closed_milestone = Milestone.objects.create(
            name='Closed Milestone',
            description='A milestone that is closed',
            date_due=date.today(),
            closed=True,
            repository=cls.repository
        )

    def test_toggle_milestone_closed_status(self):
        self.client.login(username='user_with_access', password='testpass123')
        # Closing an open milestone
        response = self.client.post(reverse('close_milestone', args=[self.repository.id, self.open_milestone.id]))
        self.open_milestone.refresh_from_db()
        self.assertTrue(self.open_milestone.closed)
        self.assertRedirects(response, reverse('repository_milestones', args=[self.repository.id]))
        # Opening a closed milestone
        response = self.client.post(reverse('close_milestone', args=[self.repository.id, self.closed_milestone.id]))
        self.closed_milestone.refresh_from_db()
        self.assertFalse(self.closed_milestone.closed)

    def test_close_milestone_without_access(self):
        self.client.login(username='user_without_access', password='testpass123')
        response = self.client.post(reverse('close_milestone', args=[self.repository.id, self.open_milestone.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())
        self.open_milestone.refresh_from_db()
        self.assertFalse(self.open_milestone.closed)

    def test_close_milestone_unauthenticated_user(self):
        response = self.client.post(reverse('close_milestone', args=[self.repository.id, self.open_milestone.id]))
        self.assertEqual(response.status_code, 302)


class DeleteMilestoneViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user_without_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.milestone = Milestone.objects.create(
            name='Milestone to Delete',
            description='Description',
            date_due=date.today(),
            repository=cls.repository
        )

    def test_delete_milestone_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('delete_milestone', args=[self.repository.id, self.milestone.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('repository_milestones', args=[self.repository.id]))
        self.assertFalse(Milestone.objects.filter(pk=self.milestone.id).exists())

    def test_delete_milestone_without_access(self):
        self.client.login(username='user_without_access', password='testpass123')
        response = self.client.post(reverse('delete_milestone', args=[self.repository.id, self.milestone.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())
        self.assertTrue(Milestone.objects.filter(pk=self.milestone.id).exists())

    def test_delete_milestone_unauthenticated_user(self):
        response = self.client.post(reverse('delete_milestone', args=[self.repository.id, self.milestone.id]))
        self.assertEqual(response.status_code, 302)
