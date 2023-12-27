from django.test import TestCase
from django.contrib.auth.models import User

from apps.pull_request.forms import PullRequestForm
from apps.repository.models import Repository
from apps.branch.models import Branch


class PullRequestFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        cls.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user, public=False)
        cls.source_branch = Branch.objects.create(name='Source Branch', repository=cls.repository)
        cls.target_branch = Branch.objects.create(name='Target Branch', repository=cls.repository)

    def test_pull_request_form_valid_data(self):
        form = PullRequestForm(data={
            'name': 'New Feature',
            'source': self.source_branch.id,
            'target': self.target_branch.id,
            'reviewers': [self.other_user.id]
        })

        form.fields['reviewers'].queryset = User.objects.all()
        self.assertTrue(form.is_valid(), form.errors)

    def test_pull_request_form_invalid_data(self):
        form = PullRequestForm(data={
            'name': '',
            'source': self.source_branch.id,
            'target': self.target_branch.id,
            'reviewers': []
        })
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('This field is required.', form.errors['name'])

    def test_pull_request_form_reviewers_queryset(self):
        form = PullRequestForm()
        form.fields['reviewers'].queryset = User.objects.all()
        self.assertIn(self.user, form.fields['reviewers'].queryset)
        self.assertIn(self.other_user, form.fields['reviewers'].queryset)

