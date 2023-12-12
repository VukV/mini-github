from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from apps.issue.models import Issue
from apps.label.models import Label
from apps.milestone.models import Milestone
from apps.project.models import Project
from apps.repository.models import Repository


class IssuesFromRepositoryViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user_without_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        Issue.objects.create(name='Test Issue', description='Test Issue Description', repository=cls.repository,
                             author=cls.user_with_access)

    def test_view_issues_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.get(reverse('repository_issues', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/issues/repository_issues.html')
        self.assertEqual(len(response.context['issues']), 1)

    def test_view_issues_without_access(self):
        self.client.login(username='user_without_access', password='testpass123')
        response = self.client.get(reverse('repository_issues', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_view_issues_unauthenticated(self):
        response = self.client.get(reverse('repository_issues', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 302)


class IssueDetailViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user_without_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.issue = Issue.objects.create(name='Test Issue', description='A test issue', repository=cls.repository,
                                         author=cls.user_with_access)

    def test_issue_detail_view_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.get(reverse('issue_detail', args=[self.repository.id, self.issue.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/issues/issue_details.html')
        self.assertEqual(response.context['issue'], self.issue)

    def test_issue_detail_view_without_access(self):
        self.client.login(username='user_without_access', password='testpass123')
        response = self.client.get(reverse('issue_detail', args=[self.repository.id, self.issue.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_issue_detail_view_unauthenticated(self):
        response = self.client.get(reverse('issue_detail', args=[self.repository.id, self.issue.id]))
        self.assertEqual(response.status_code, 302)


class CloseIssueViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user_without_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.issue = Issue.objects.create(
            name='Test Issue',
            description='A test issue',
            repository=cls.repository,
            author=cls.user_with_access
        )

    def test_toggle_issue_closed_status(self):
        self.client.login(username='user_with_access', password='testpass123')

        response = self.client.post(reverse('close_issue', args=[self.repository.id, self.issue.id]))
        self.issue.refresh_from_db()
        self.assertTrue(self.issue.closed)
        self.assertRedirects(response, reverse('issue_detail', args=[self.repository.id, self.issue.id]))

        response = self.client.post(reverse('close_issue', args=[self.repository.id, self.issue.id]))
        self.issue.refresh_from_db()
        self.assertFalse(self.issue.closed)

    def test_close_issue_without_access(self):
        self.client.login(username='user_without_access', password='testpass123')
        response = self.client.post(reverse('close_issue', args=[self.repository.id, self.issue.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())
        self.issue.refresh_from_db()
        self.assertFalse(self.issue.closed)

    def test_close_issue_unauthenticated_user(self):
        response = self.client.post(reverse('close_issue', args=[self.repository.id, self.issue.id]))
        self.assertEqual(response.status_code, 302)


class DeleteIssueViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user_without_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.issue = Issue.objects.create(
            name='Test Issue',
            description='A test issue',
            repository=cls.repository,
            author=cls.user_with_access
        )

    def test_delete_issue_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('delete_issue', args=[self.repository.id, self.issue.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('repository_issues', args=[self.repository.id]))
        self.assertFalse(Issue.objects.filter(pk=self.issue.id).exists())

    def test_delete_issue_without_access(self):
        self.client.login(username='user_without_access', password='testpass123')
        response = self.client.post(reverse('delete_issue', args=[self.repository.id, self.issue.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())
        self.assertTrue(Issue.objects.filter(pk=self.issue.id).exists())

    def test_delete_issue_unauthenticated_user(self):
        response = self.client.post(reverse('delete_issue', args=[self.repository.id, self.issue.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Issue.objects.filter(pk=self.issue.id).exists())


class AddIssueViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.project = Project.objects.create(name='Test Project', repository=cls.repository)
        cls.milestone = Milestone.objects.create(name='Test Milestone', date_due=timezone.now() + timedelta(days=10),
                                                 repository=cls.repository)
        cls.label = Label.objects.create(name='Test Label', repository=cls.repository)

    def test_add_issue_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        form_data = {
            'name': 'New Issue',
            'description': 'Description of New Issue',
            'project': self.project.id,
            'milestone': self.milestone.id,
            'labels': [self.label.id]
        }
        response = self.client.post(reverse('add_issue', args=[self.repository.id]), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('repository_issues', args=[self.repository.id]))
        self.assertEqual(Issue.objects.count(), 1)

    def test_add_issue_without_access(self):
        User.objects.create_user(username='other_user', password='testpass123')
        self.client.login(username='other_user', password='testpass123')
        response = self.client.post(reverse('add_issue', args=[self.repository.id]), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_add_issue_unauthenticated_user(self):
        response = self.client.get(reverse('add_issue', args=[self.repository.id]))
        self.assertEqual(response.status_code, 302)

    # TODO: test edit
