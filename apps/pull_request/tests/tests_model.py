from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from apps.pull_request.models import PullRequest, PullRequestStatus
from apps.repository.models import Repository
from apps.branch.models import Branch
from apps.label.models import Label


class PullRequestModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user, public=False)
        cls.source_branch = Branch.objects.create(name='Source Branch', repository=cls.repository)
        cls.target_branch = Branch.objects.create(name='Target Branch', repository=cls.repository)
        cls.label = Label.objects.create(name='Bug', repository=cls.repository)

        cls.pull_request = PullRequest.objects.create(
            name='New Feature',
            source=cls.source_branch,
            target=cls.target_branch,
            author=cls.user,
            reviewed=False,
            status=PullRequestStatus.OPEN.value,
            repository=cls.repository
        )
        cls.pull_request.labels.add(cls.label)
        cls.pull_request.reviewers.add(cls.user)

    def test_pull_request_creation(self):
        self.assertEqual(self.pull_request.name, 'New Feature')
        self.assertEqual(self.pull_request.source, self.source_branch)
        self.assertEqual(self.pull_request.target, self.target_branch)
        self.assertEqual(self.pull_request.author, self.user)
        self.assertIn(self.user, self.pull_request.reviewers.all())
        self.assertIn(self.label, self.pull_request.labels.all())
        self.assertFalse(self.pull_request.reviewed)
        self.assertEqual(self.pull_request.status, PullRequestStatus.OPEN.value)
        self.assertEqual(self.pull_request.repository, self.repository)

    def test_pull_request_default_date_created(self):
        self.assertIsNotNone(self.pull_request.date_created)
        self.assertTrue(isinstance(self.pull_request.date_created, timezone.datetime))

    def test_string_representation(self):
        expected_string = 'New Feature by testuser'
        self.assertEqual(str(self.pull_request), expected_string)
