from django.test import TestCase
from datetime import date
from django.contrib.auth.models import User
from apps.issue.models import Issue
from apps.milestone.models import Milestone
from apps.repository.models import Repository


class MilestoneModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.owner)
        cls.milestone = Milestone.objects.create(
            name='Milestone 1',
            description='First Milestone',
            date_due=date.today(),
            repository=cls.repository
        )
        
        cls.open_issue = Issue.objects.create(
            milestone=cls.milestone,
            closed=False,
            author=cls.owner,
            repository=cls.repository
        )
        cls.closed_issue = Issue.objects.create(
            milestone=cls.milestone,
            closed=True,
            author=cls.owner,
            repository=cls.repository
        )

    def test_string_representation(self):
        self.assertEqual(str(self.milestone), 'Milestone 1')

    def test_get_issue_count(self):
        self.assertEqual(self.milestone.get_issue_count(), 2)

    def test_get_closed_issue_count(self):
        self.assertEqual(self.milestone.get_closed_issue_count(), 1)

    def test_set_closed(self):
        self.milestone.set_closed(True)
        self.assertTrue(self.milestone.closed)
        self.assertEqual(self.milestone.date_closed, date.today())

    def test_is_complete_no_issues(self):
        empty_milestone = Milestone.objects.create(
            name='Empty Milestone',
            description='No Issues',
            date_due=date.today(),
            repository=self.repository
        )
        self.assertFalse(empty_milestone.is_complete())

    def test_is_complete_with_open_and_closed_issues(self):
        self.assertFalse(self.milestone.is_complete())

    def test_is_complete_with_all_closed_issues(self):
        self.milestone.issues.all().update(closed=True)
        self.assertTrue(self.milestone.is_complete())

    def test_get_complete_percentage(self):
        self.assertEqual(self.milestone.get_complete_percentage(), 50)
        self.milestone.issues.all().update(closed=True)
        self.assertEqual(self.milestone.get_complete_percentage(), 100)
