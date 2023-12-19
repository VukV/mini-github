from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.project.models import Project
from apps.repository.models import Repository
from apps.issue.models import Issue, IssueStatus


class ProjectsFromRepositoryViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user_without_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        Project.objects.create(name='Test Project', description='A test project', repository=cls.repository)

    def test_view_projects_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.get(reverse('repository_projects', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/projects/repository_projects.html')
        self.assertEqual(len(response.context['projects']), 1)

    def test_view_projects_without_access(self):
        self.client.login(username='user_without_access', password='testpass123')
        response = self.client.get(reverse('repository_projects', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_view_projects_unauthenticated(self):
        response = self.client.get(reverse('repository_projects', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 302)


class ProjectDetailViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user_without_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.project = Project.objects.create(name='Test Project', repository=cls.repository)
        Issue.objects.create(name='Test Issue TODO', repository=cls.repository, author=cls.user_with_access, project=cls.project, status=IssueStatus.TODO.name)
        Issue.objects.create(name='Test Issue IN_PROGRESS', repository=cls.repository, author=cls.user_with_access, project=cls.project, status=IssueStatus.IN_PROGRESS.name)
        Issue.objects.create(name='Test Issue DONE', repository=cls.repository, author=cls.user_with_access, project=cls.project, status=IssueStatus.DONE.name)

    def test_project_detail_view_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.get(reverse('project_detail', args=[self.repository.id, self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/projects/project_details.html')
        self.assertEqual(response.context['project'], self.project)
        self.assertEqual(len(response.context['todo_issues']), 1)
        self.assertEqual(len(response.context['in_progress_issues']), 1)
        self.assertEqual(len(response.context['done_issues']), 1)

    def test_project_detail_view_without_access(self):
        self.client.login(username='user_without_access', password='testpass123')
        response = self.client.get(reverse('project_detail', args=[self.repository.id, self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_project_detail_view_unauthenticated(self):
        response = self.client.get(reverse('project_detail', args=[self.repository.id, self.project.id]))
        self.assertEqual(response.status_code, 302)


class AddProjectViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)

    def test_add_project_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        form_data = {
            'name': 'New Project',
            'description': 'Description of New Project'
        }
        response = self.client.post(reverse('add_project', args=[self.repository.id]), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('repository_projects', args=[self.repository.id]))
        self.assertEqual(Project.objects.count(), 1)

    def test_add_project_without_access(self):
        other_user = User.objects.create_user(username='other_user', password='testpass123')
        self.client.login(username='other_user', password='testpass123')
        response = self.client.post(reverse('add_project', args=[self.repository.id]), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_add_project_invalid_form(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('add_project', args=[self.repository.id]), {
            'name': '',
            'description': 'Some description'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('This field is required.', response.content.decode())

    def test_add_project_unauthenticated_user(self):
        response = self.client.get(reverse('add_project', args=[self.repository.id]))
        self.assertEqual(response.status_code, 302)


class EditProjectViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.project = Project.objects.create(name='Original Project', description='Original Description', repository=cls.repository)

    def test_edit_project_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        updated_data = {
            'name': 'Updated Project',
            'description': 'Updated Description'
        }
        response = self.client.post(reverse('edit_project', args=[self.repository.id, self.project.id]), updated_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('project_detail', args=[self.repository.id, self.project.id]))
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Updated Project')
        self.assertEqual(self.project.description, 'Updated Description')

    def test_edit_project_without_access(self):
        other_user = User.objects.create_user(username='other_user', password='testpass123')
        self.client.login(username='other_user', password='testpass123')
        response = self.client.post(reverse('edit_project', args=[self.repository.id, self.project.id]), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_edit_project_invalid_form(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('edit_project', args=[self.repository.id, self.project.id]), {
            'name': '',
            'description': 'Updated Description'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid form', response.content.decode())

    def test_edit_project_unauthenticated_user(self):
        response = self.client.get(reverse('edit_project', args=[self.repository.id, self.project.id]))
        self.assertEqual(response.status_code, 302)


class DeleteProjectViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.project = Project.objects.create(name='Test Project', description='A test project', repository=cls.repository)

    def test_delete_project_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('delete_project', args=[self.repository.id, self.project.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('repository_projects', args=[self.repository.id]))
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_delete_project_without_access(self):
        other_user = User.objects.create_user(username='other_user', password='testpass123')
        self.client.login(username='other_user', password='testpass123')
        response = self.client.post(reverse('delete_project', args=[self.repository.id, self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())
        self.assertTrue(Project.objects.filter(pk=self.project.id).exists())

    def test_delete_project_unauthenticated_user(self):
        response = self.client.post(reverse('delete_project', args=[self.repository.id, self.project.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(pk=self.project.id).exists())
