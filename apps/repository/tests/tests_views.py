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
