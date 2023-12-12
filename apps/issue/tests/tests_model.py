from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.issue.models import Issue, IssueStatus
from apps.label.models import Label
from apps.milestone.models import Milestone
from apps.project.models import Project
from apps.repository.models import Repository


class IssueModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user)
        cls.project = Project.objects.create(name='Test Project', repository=cls.repository)
        cls.milestone = Milestone.objects.create(name='Test Milestone', date_due=timezone.now() + timedelta(days=10), repository=cls.repository)
        cls.label = Label.objects.create(name='Test Label', repository=cls.repository)
        cls.issue = Issue.objects.create(
            name='Test Issue',
            description='Test Issue Description',
            repository=cls.repository,
            author=cls.user,
            project=cls.project,
            milestone=cls.milestone
        )
        cls.issue.labels.add(cls.label)

    def test_string_representation(self):
        self.assertEqual(str(self.issue), 'Test Issue')

    def test_change_closed(self):
        self.issue.change_closed()
        self.assertTrue(self.issue.closed)

        self.issue.change_closed()
        self.assertFalse(self.issue.closed)

    def test_change_status(self):
        self.issue.change_status(IssueStatus.DONE.name)
        self.assertEqual(self.issue.status, IssueStatus.DONE.name)
        self.assertTrue(self.issue.closed)
