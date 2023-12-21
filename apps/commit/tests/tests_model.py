from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from apps.commit.models import Commit
from apps.repository.models import Repository
from apps.branch.models import Branch


class CommitModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user)
        cls.branch = Branch.objects.create(name='Main Branch', repository=cls.repository)

        cls.commit = Commit.objects.create(
            hash='abcd1234',
            message='Initial commit',
            author=cls.user,
            repository=cls.repository,
            date_time_created=timezone.now()
        )
        cls.commit.branches.add(cls.branch)

    def test_commit_creation(self):
        self.assertEqual(self.commit.hash, 'abcd1234')
        self.assertEqual(self.commit.message, 'Initial commit')
        self.assertEqual(self.commit.author, self.user)
        self.assertEqual(self.commit.repository, self.repository)
        self.assertIn(self.branch, self.commit.branches.all())

    def test_commit_default_values(self):
        self.assertIsNotNone(self.commit.date_time_created)
