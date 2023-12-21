from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.branch.models import Branch
from apps.commit.models import Commit
from apps.repository.models import Repository


class CommitsFromBranchViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user_without_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.branch = Branch.objects.create(name='Main Branch', repository=cls.repository)

        cls.commit = Commit.objects.create(
            hash='abcd1234',
            message='Initial commit',
            repository=cls.repository,
            author=cls.user_with_access
        )

        cls.commit.branches.add(cls.branch)

    def test_view_commits_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.get(reverse('branch_commits', args=[self.branch.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/commits/branch_commits.html')
        self.assertEqual(len(response.context['commits']), 1)

    def test_view_commits_without_access(self):
        self.client.login(username='user_without_access', password='testpass123')
        response = self.client.get(reverse('branch_commits', args=[self.branch.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_view_commits_unauthenticated(self):
        response = self.client.get(reverse('branch_commits', args=[self.branch.pk]))
        self.assertEqual(response.status_code, 302)


class AddCommitViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.branch = Branch.objects.create(name='Main Branch', repository=cls.repository)

    def test_add_commit_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        form_data = {
            'message': 'New commit message'
        }
        response = self.client.post(reverse('add_commit', args=[self.branch.id]), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('branch_commits', args=[self.branch.id]))
        self.assertEqual(Commit.objects.count(), 1)
        commit = Commit.objects.first()
        self.assertEqual(commit.message, 'New commit message')
        self.assertEqual(commit.author, self.user_with_access)
        self.assertIn(self.branch, commit.branches.all())

    def test_add_commit_without_access(self):
        other_user = User.objects.create_user(username='other_user', password='testpass123')
        self.client.login(username='other_user', password='testpass123')
        response = self.client.post(reverse('add_commit', args=[self.branch.id]), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_add_commit_invalid_form(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('add_commit', args=[self.branch.id]), {'message': ''})  # Intentionally invalid
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid form.', response.content.decode())

    def test_add_commit_unauthenticated_user(self):
        response = self.client.get(reverse('add_commit', args=[self.branch.id]))
        self.assertEqual(response.status_code, 302)
