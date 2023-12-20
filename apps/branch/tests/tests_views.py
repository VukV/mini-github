from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from apps.repository.models import Repository
from apps.branch.models import Branch


class BranchesFromRepositoryViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user_without_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        Branch.objects.create(name='Main Branch', default=True, repository=cls.repository)
        Branch.objects.create(name='Feature Branch', default=False, repository=cls.repository)

    def test_view_branches_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.get(reverse('repository_branches', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/branches/repository_branches.html')
        self.assertEqual(len(response.context['branches']), 2)

    def test_view_branches_without_access(self):
        self.client.login(username='user_without_access', password='testpass123')
        response = self.client.get(reverse('repository_branches', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_view_branches_unauthenticated(self):
        response = self.client.get(reverse('repository_branches', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 302)


class AddBranchViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)

    def test_add_branch_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        form_data = {
            'name': 'New Branch'
        }
        response = self.client.post(reverse('add_branch', args=[self.repository.id]), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('repository_branches', args=[self.repository.id]))
        self.assertEqual(Branch.objects.count(), 1)
        self.assertEqual(Branch.objects.first().name, 'New Branch')

    def test_add_branch_without_access(self):
        other_user = User.objects.create_user(username='other_user', password='testpass123')
        self.client.login(username='other_user', password='testpass123')
        response = self.client.post(reverse('add_branch', args=[self.repository.id]), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_add_branch_invalid_form(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('add_branch', args=[self.repository.id]), {'name': ''})  # Intentionally invalid
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid form.', response.content.decode())

    def test_add_branch_unauthenticated_user(self):
        response = self.client.get(reverse('add_branch', args=[self.repository.id]))
        self.assertEqual(response.status_code, 302)


class EditBranchViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.branch = Branch.objects.create(name='Original Branch', repository=cls.repository)

    def test_edit_branch_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        updated_data = {
            'name': 'Updated Branch'
        }
        response = self.client.post(reverse('edit_branch', args=[self.repository.id, self.branch.id]), updated_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('repository_branches', args=[self.repository.id]))
        self.branch.refresh_from_db()
        self.assertEqual(self.branch.name, 'Updated Branch')

    def test_edit_branch_without_access(self):
        other_user = User.objects.create_user(username='other_user', password='testpass123')
        self.client.login(username='other_user', password='testpass123')
        response = self.client.post(reverse('edit_branch', args=[self.repository.id, self.branch.id]), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_edit_branch_invalid_form(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('edit_branch', args=[self.repository.id, self.branch.id]), {'name': ''})  # Intentionally invalid
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid form', response.content.decode())

    def test_edit_branch_unauthenticated_user(self):
        response = self.client.get(reverse('edit_branch', args=[self.repository.id, self.branch.id]))
        self.assertEqual(response.status_code, 302)


class DeleteBranchViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.default_branch = Branch.objects.create(name='Main Branch', default=True, repository=cls.repository)
        cls.non_default_branch = Branch.objects.create(name='Feature Branch', default=False, repository=cls.repository)

    def test_delete_non_default_branch_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('delete_branch', args=[self.repository.id, self.non_default_branch.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('repository_branches', args=[self.repository.id]))
        self.assertFalse(Branch.objects.filter(pk=self.non_default_branch.id).exists())

    def test_delete_default_branch_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('delete_branch', args=[self.repository.id, self.default_branch.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You can not delete a default branch.', response.content.decode())

    def test_delete_branch_without_access(self):
        other_user = User.objects.create_user(username='other_user', password='testpass123')
        self.client.login(username='other_user', password='testpass123')
        response = self.client.post(reverse('delete_branch', args=[self.repository.id, self.non_default_branch.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_delete_branch_unauthenticated_user(self):
        response = self.client.post(reverse('delete_branch', args=[self.repository.id, self.non_default_branch.id]))
        self.assertEqual(response.status_code, 302)
