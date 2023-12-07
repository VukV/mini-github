from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from apps.issue.models import Issue
from apps.label.models import Label
from apps.pull_request.models import PullRequest
from apps.repository.models import Repository


class LabelViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user1', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user2', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        Label.objects.create(name='Test Label', repository=cls.repository)

    def test_labels_view_with_access(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('repository_labels', args=[self.repository.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/labels/repository_labels.html')
        self.assertIn('Test Label', response.content.decode())

    def test_labels_view_without_access(self):
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('repository_labels', args=[self.repository.id]))
        print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_labels_view_nonexistent_repository(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('repository_labels', args=[999]))
        self.assertEqual(response.status_code, 404)


class AddLabelViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user1', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user2', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)

    def test_add_label_page_load_with_access(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('add_label', args=[self.repository.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/labels/add_label.html')

    def test_add_label_page_load_without_access(self):
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('add_label', args=[self.repository.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_add_label_valid_post_request(self):
        self.client.login(username='user1', password='testpass123')
        label_count_before = Label.objects.count()
        response = self.client.post(reverse('add_label', args=[self.repository.id]), {
            'name': 'New Label',
            'description': 'A new label',
            'color': '#FFFFFF'
        })
        label_count_after = Label.objects.count()
        self.assertEqual(label_count_after, label_count_before + 1)
        self.assertRedirects(response, reverse('repository_labels', args=[self.repository.id]))

    def test_add_label_invalid_post_request(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('add_label', args=[self.repository.id]), {
            'name': '',
            'description': 'Invalid label',
            'color': '#FFFFFF'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('This field is required.', response.content.decode())

    def test_add_label_nonexistent_repository(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('add_label', args=[999]))  # Assuming 999 is a nonexistent repository ID
        self.assertEqual(response.status_code, 404)


class EditLabelViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user1', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user2', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.label = Label.objects.create(name='Test Label', description='A test label', color='#FFFFFF', repository=cls.repository)

    def test_edit_label_page_load_with_access(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('edit_label', args=[self.repository.id, self.label.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/labels/edit_label.html')

    def test_edit_label_page_load_without_access(self):
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('edit_label', args=[self.repository.id, self.label.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_edit_label_valid_post_request(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('edit_label', args=[self.repository.id, self.label.id]), {
            'name': 'Updated Label',
            'description': 'An updated test label',
            'color': '#000000'
        })
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, 'Updated Label')
        self.assertRedirects(response, reverse('repository_labels', args=[self.repository.id]))

    def test_edit_label_invalid_post_request(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('edit_label', args=[self.repository.id, self.label.id]), {
            'name': '',
            'description': 'An updated test label',
            'color': '#000000'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue('name' in response.context['form'].errors)

    def test_edit_label_nonexistent_repository(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('edit_label', args=[999, self.label.id]))
        self.assertEqual(response.status_code, 404)

    def test_edit_label_nonexistent_label(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('edit_label', args=[self.repository.id, 999]))
        self.assertEqual(response.status_code, 404)


class DeleteLabelViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user1', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user2', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.label = Label.objects.create(name='Test Label', description='A test label', color='#FFFFFF', repository=cls.repository)

    def test_delete_label_with_access(self):
        self.client.login(username='user1', password='testpass123')
        label_count_before = Label.objects.count()
        response = self.client.post(reverse('delete_label', args=[self.repository.id, self.label.id]))
        label_count_after = Label.objects.count()
        self.assertEqual(label_count_after, label_count_before - 1)
        self.assertRedirects(response, reverse('repository_labels', args=[self.repository.id]))

    def test_delete_label_without_access(self):
        self.client.login(username='user2', password='testpass123')
        response = self.client.post(reverse('delete_label', args=[self.repository.id, self.label.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_delete_label_in_use_by_issue(self):
        issue = Issue.objects.create(name='Test Issue', repository=self.repository, author_id=self.user_with_access.id)
        self.label.issues.add(issue)
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('delete_label', args=[self.repository.id, self.label.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Label is in use by issue(s).', response.content.decode())

    def test_delete_label_nonexistent_label(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('delete_label', args=[self.repository.id, 999]))
        self.assertEqual(response.status_code, 404)
