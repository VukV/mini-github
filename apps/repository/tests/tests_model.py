from django.contrib.auth.models import User
from django.test import TestCase
from apps.repository.models import Repository


class RepositoryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_create_repository(self):
        repository = Repository.objects.create(
            name='New Repository',
            public=True,
            owner=self.user
        )
        self.assertIsInstance(repository, Repository)
        self.assertEqual(repository.name, 'New Repository')
        self.assertTrue(repository.public)
        self.assertEqual(repository.owner, self.user)


class RepositoryModelMethodsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='testpass123')
        cls.collaborator = User.objects.create_user(username='collab', password='testpass123')
        cls.other_user = User.objects.create_user(username='other', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', public=False, owner=cls.owner)
        cls.repository.collaborators.add(cls.collaborator)

    def test_string_representation(self):
        self.assertEqual(str(self.repository), 'Test Repo')

    def test_check_access_public_repository(self):
        public_repo = Repository.objects.create(name='Public Repo', public=True, owner=self.owner)
        self.assertTrue(public_repo.check_access(self.other_user))

    def test_check_access_private_repository_owner(self):
        self.assertTrue(self.repository.check_access(self.owner))

    def test_check_access_private_repository_collaborator(self):
        self.assertTrue(self.repository.check_access(self.collaborator))

    def test_check_access_private_repository_other_user(self):
        self.assertFalse(self.repository.check_access(self.other_user))
