from django.test import TestCase
from apps.project.models import Project
from apps.repository.models import Repository
from django.contrib.auth.models import User


class ProjectModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user)
        cls.project = Project.objects.create(
            name='Test Project',
            description='Test Project Description',
            repository=cls.repository
        )

    def test_string_representation(self):
        self.assertEqual(str(self.project), 'Test Project')

    def test_project_fields(self):
        self.assertEqual(self.project.name, 'Test Project')
        self.assertEqual(self.project.description, 'Test Project Description')
        self.assertEqual(self.project.repository, self.repository)
