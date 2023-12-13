from django.test import TestCase
from apps.project.forms import ProjectForm
from apps.repository.models import Repository
from django.contrib.auth.models import User


class ProjectFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user)

    def test_project_form_valid_data(self):
        form_data = {
            'name': 'Test Project',
            'description': 'A test project description'
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_project_form_invalid_data(self):
        form_data = {
            'name': '',
            'description': 'A test project description'
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_project_form_missing_description(self):
        form_data = {
            'name': 'Test Project',
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

