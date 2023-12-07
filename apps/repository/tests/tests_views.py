from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from apps.repository.models import Repository


class RepositoryDetailViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='testpass123')
        cls.other_user = User.objects.create_user(username='other_user', password='testpass123')
        cls.public_repository = Repository.objects.create(name='Public Repo', public=True, owner=cls.owner)
        cls.private_repository = Repository.objects.create(name='Private Repo', public=False, owner=cls.owner)

    def test_repository_detail_view_with_owner(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.get(reverse('repository', args=[self.public_repository.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/repository.html')

    def test_repository_detail_view_with_other_user_public_repo(self):
        self.client.login(username='other_user', password='testpass123')
        response = self.client.get(reverse('repository', args=[self.public_repository.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/repository.html')

    def test_repository_detail_view_with_other_user_private_repo(self):
        self.client.login(username='other_user', password='testpass123')
        response = self.client.get(reverse('repository', args=[self.private_repository.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_repository_detail_view_unauthenticated_user(self):
        response = self.client.get(reverse('repository', args=[self.public_repository.id]))
        self.assertEqual(response.status_code, 302)


class CreateRepositoryViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_create_repository_view_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('create_repository'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/repository_create.html')

    def test_create_repository_view_post_valid_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('create_repository'), {
            'name': 'New Repository',
            'public': True
        })
        self.assertEqual(Repository.objects.count(), 1)
        new_repository = Repository.objects.first()
        self.assertEqual(new_repository.name, 'New Repository')
        self.assertTrue(new_repository.public)
        self.assertEqual(new_repository.owner, self.user)
        self.assertRedirects(response, reverse('repository', args=[new_repository.id]))

    def test_create_repository_view_post_invalid_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('create_repository'), {
            'name': '',
            'public': True
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('This field is required.', response.content.decode())
        self.assertEqual(Repository.objects.count(), 0)


class RepositorySettingsViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='testpass123')
        cls.non_owner = User.objects.create_user(username='non_owner', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', public=True, owner=cls.owner)

    def test_repository_settings_view_with_owner(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.get(reverse('repository_settings', args=[self.repository.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/repository_settings.html')

    def test_repository_settings_view_with_non_owner(self):
        self.client.login(username='non_owner', password='testpass123')
        response = self.client.get(reverse('repository_settings', args=[self.repository.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to repository settings.', response.content.decode())

    def test_repository_settings_view_unauthenticated_access(self):
        response = self.client.get(reverse('repository_settings', args=[self.repository.id]))
        self.assertEqual(response.status_code, 302)


class DeleteRepositoryViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='testpass123')
        cls.non_owner = User.objects.create_user(username='non_owner', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', public=True, owner=cls.owner)

    def test_delete_repository_view_with_owner(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(reverse('delete_repository', args=[self.repository.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertFalse(Repository.objects.filter(pk=self.repository.id).exists())

    def test_delete_repository_view_with_non_owner(self):
        self.client.login(username='non_owner', password='testpass123')
        response = self.client.post(reverse('delete_repository', args=[self.repository.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have permission to delete this repository.', response.content.decode())
        self.assertTrue(Repository.objects.filter(pk=self.repository.id).exists())

    def test_delete_repository_view_unauthenticated_access(self):
        response = self.client.post(reverse('delete_repository', args=[self.repository.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Repository.objects.filter(pk=self.repository.id).exists())


class ChangeRepositoryVisibilityViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='testpass123')
        cls.non_owner = User.objects.create_user(username='non_owner', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', public=True, owner=cls.owner)

    def test_change_visibility_with_owner(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(reverse('change_repository_visibility', args=[self.repository.id]), {'visibility': 'private'})
        self.repository.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('repository_settings', args=[self.repository.id]))
        self.assertFalse(self.repository.public)

    def test_change_visibility_with_non_owner(self):
        self.client.login(username='non_owner', password='testpass123')
        response = self.client.post(reverse('change_repository_visibility', args=[self.repository.id]), {'visibility': 'private'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have permission to change visibility.', response.content.decode())
        self.repository.refresh_from_db()
        self.assertTrue(self.repository.public)

    def test_change_visibility_unauthenticated_access(self):
        response = self.client.post(reverse('change_repository_visibility', args=[self.repository.id]), {'visibility': 'private'})
        self.assertEqual(response.status_code, 302)
        self.repository.refresh_from_db()
        self.assertTrue(self.repository.public)


class RenameRepositoryViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='testpass123')
        cls.non_owner = User.objects.create_user(username='non_owner', password='testpass123')
        cls.repository = Repository.objects.create(name='Old Repo Name', public=True, owner=cls.owner)

    def test_rename_repository_with_owner(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(reverse('rename_repository', args=[self.repository.id]), {'name': 'New Repo Name'})
        self.repository.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('repository_settings', args=[self.repository.id]))
        self.assertEqual(self.repository.name, 'New Repo Name')

    def test_rename_repository_with_non_owner(self):
        self.client.login(username='non_owner', password='testpass123')
        response = self.client.post(reverse('rename_repository', args=[self.repository.id]), {'name': 'New Repo Name'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have permission to change repository name.', response.content.decode())
        self.repository.refresh_from_db()
        self.assertEqual(self.repository.name, 'Old Repo Name')

    def test_rename_repository_unauthenticated_access(self):
        response = self.client.post(reverse('rename_repository', args=[self.repository.id]), {'name': 'New Repo Name'})
        self.assertEqual(response.status_code, 302)
        self.repository.refresh_from_db()
        self.assertEqual(self.repository.name, 'Old Repo Name')


class AddCollaboratorViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='testpass123')
        cls.user_to_add = User.objects.create_user(username='new_collab', password='testpass123')
        cls.non_owner = User.objects.create_user(username='non_owner', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', public=True, owner=cls.owner)

    def test_add_collaborator_with_owner(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(reverse('add_collaborator', args=[self.repository.id]), {'username': 'new_collab'})
        self.repository.refresh_from_db()
        self.assertIn(self.user_to_add, self.repository.collaborators.all())
        self.assertRedirects(response, reverse('repository_settings', args=[self.repository.id]))

    def test_add_collaborator_with_non_owner(self):
        self.client.login(username='non_owner', password='testpass123')
        response = self.client.post(reverse('add_collaborator', args=[self.repository.id]), {'username': 'new_collab'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have permission to change repository name.', response.content.decode())
        self.repository.refresh_from_db()
        self.assertNotIn(self.user_to_add, self.repository.collaborators.all())

    def test_add_collaborator_user_not_exist(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(reverse('add_collaborator', args=[self.repository.id]), {'username': 'nonexistent_user'})
        self.assertRedirects(response, reverse('repository_settings', args=[self.repository.id]))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'User does not exist.')

    def test_add_collaborator_unauthenticated_access(self):
        response = self.client.post(reverse('add_collaborator', args=[self.repository.id]), {'username': 'new_collab'})
        self.assertEqual(response.status_code, 302)


class RemoveCollaboratorViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='testpass123')
        cls.collaborator = User.objects.create_user(username='collaborator', password='testpass123')
        cls.non_owner = User.objects.create_user(username='non_owner', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', public=True, owner=cls.owner)
        cls.repository.collaborators.add(cls.collaborator)

    def test_remove_collaborator_with_owner(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(reverse('remove_collaborator', args=[self.repository.id, self.collaborator.id]))
        self.repository.refresh_from_db()
        self.assertNotIn(self.collaborator, self.repository.collaborators.all())
        self.assertRedirects(response, reverse('repository_settings', args=[self.repository.id]))

    def test_remove_collaborator_with_non_owner(self):
        self.client.login(username='non_owner', password='testpass123')
        response = self.client.post(reverse('remove_collaborator', args=[self.repository.id, self.collaborator.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have permission to change repository name.', response.content.decode())
        self.repository.refresh_from_db()
        self.assertIn(self.collaborator, self.repository.collaborators.all())

    def test_remove_nonexistent_collaborator(self):
        self.client.login(username='owner', password='testpass123')
        nonexistent_user_id = self.collaborator.id + 100  # Assuming this ID doesn't exist
        response = self.client.post(reverse('remove_collaborator', args=[self.repository.id, nonexistent_user_id]))
        self.assertRedirects(response, reverse('repository_settings', args=[self.repository.id]))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'User does not exist.')

    def test_remove_collaborator_unauthenticated_access(self):
        response = self.client.post(reverse('remove_collaborator', args=[self.repository.id, self.collaborator.id]))
        self.assertEqual(response.status_code, 302)
