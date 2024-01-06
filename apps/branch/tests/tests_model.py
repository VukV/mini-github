from django.test import TestCase
from apps.repository.models import Repository
from apps.branch.models import Branch
from django.contrib.auth.models import User


class BranchModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user)
        Branch.objects.create(name='main', default=True, repository=cls.repository)

    def test_create_branch(self):
        branch = Branch.objects.get(name='main')
        self.assertEqual(branch.name, 'main')
        self.assertTrue(branch.default)
        self.assertEqual(branch.repository, self.repository)

    def test_string_representation(self):
        branch = Branch.objects.get(name='main')
        self.assertEqual(str(branch), 'main')
