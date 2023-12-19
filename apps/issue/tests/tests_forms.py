from django.test import TestCase

from django.contrib.auth.models import User

from apps.issue.forms import IssueForm
from apps.label.models import Label
from apps.milestone.models import Milestone
from apps.project.models import Project
from apps.repository.models import Repository


class IssueFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user)
        cls.project = Project.objects.create(name='Test Project', repository=cls.repository)
        cls.milestone = Milestone.objects.create(name='Test Milestone', repository=cls.repository, date_due='2023-01-01')
        cls.label = Label.objects.create(name='Test Label', repository=cls.repository, color='#FFFFFF')

    def test_issue_form_valid_data(self):
        form_data = {
            'name': 'New Issue',
            'description': 'Description of New Issue',
            'project': self.project.id,
            'milestone': self.milestone.id,
            'labels': [self.label.id],
            'assignees': [self.user.id]
        }
        form = IssueForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_issue_form_invalid_data(self):
        form_data = {
            'name': '',
            'description': '',
        }
        form = IssueForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
