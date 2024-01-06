from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from apps.branch.models import Branch
from apps.repository.models import Repository
from apps.pull_request.models import PullRequest, PullRequestStatus


class PullRequestsFromRepositoryViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user_without_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)

        cls.source_branch = Branch.objects.create(name='Source Branch', repository=cls.repository)
        cls.target_branch = Branch.objects.create(name='Target Branch', repository=cls.repository)

        PullRequest.objects.create(name='Open PR', repository=cls.repository, status=PullRequestStatus.OPEN.value,
                                   source=cls.source_branch, target=cls.target_branch)
        PullRequest.objects.create(name='Merged PR', repository=cls.repository, status=PullRequestStatus.MERGED.value,
                                   source=cls.source_branch, target=cls.target_branch)
        PullRequest.objects.create(name='Closed PR', repository=cls.repository, status=PullRequestStatus.CLOSED.value,
                                   source=cls.source_branch, target=cls.target_branch)

    def test_view_pull_requests_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.get(reverse('repository_pull_requests', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'repository/pull_requests/repository_pull_requests.html')
        self.assertEqual(len(response.context['pr_open']), 1)
        self.assertEqual(len(response.context['pr_merged']), 1)
        self.assertEqual(len(response.context['pr_closed']), 1)

    def test_view_pull_requests_without_access(self):
        self.client.login(username='user_without_access', password='testpass123')
        response = self.client.get(reverse('repository_pull_requests', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_view_pull_requests_unauthenticated(self):
        response = self.client.get(reverse('repository_pull_requests', args=[self.repository.pk]))
        self.assertEqual(response.status_code, 302)


class PullRequestDetailViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.user_without_access = User.objects.create_user(username='user_without_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.source_branch = Branch.objects.create(name='Source Branch', repository=cls.repository)
        cls.target_branch = Branch.objects.create(name='Target Branch', repository=cls.repository)
        cls.pull_request = PullRequest.objects.create(
            name='Example PR',
            repository=cls.repository,
            source=cls.source_branch,
            target=cls.target_branch,
            status=PullRequestStatus.OPEN.value
        )

    def test_pull_request_detail_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.get(reverse('pull_request_detail', args=[self.repository.id, self.pull_request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.pull_request.name)

    def test_pull_request_detail_without_access(self):
        self.client.login(username='user_without_access', password='testpass123')
        response = self.client.get(reverse('pull_request_detail', args=[self.repository.id, self.pull_request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_pull_request_detail_unauthenticated(self):
        response = self.client.get(reverse('pull_request_detail', args=[self.repository.id, self.pull_request.id]))
        self.assertEqual(response.status_code, 302)

    def test_nonexistent_pull_request(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.get(reverse('pull_request_detail', args=[self.repository.id, 9999]))  # Non-existent PR ID
        self.assertEqual(response.status_code, 404)


class AddPullRequestViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.source_branch = Branch.objects.create(name='Source Branch', repository=cls.repository)
        cls.target_branch = Branch.objects.create(name='Target Branch', repository=cls.repository)

    def test_add_pull_request_with_access(self):
        self.client.login(username='user_with_access', password='testpass123')
        form_data = {
            'name': 'New PR',
            'source': self.source_branch.id,
            'target': self.target_branch.id,
        }
        response = self.client.post(reverse('add_pull_request', args=[self.repository.id]), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PullRequest.objects.filter(name='New PR').exists())

    def test_add_pull_request_form_invalid(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('add_pull_request', args=[self.repository.id]), {})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'name', 'This field is required.')

    def test_add_pull_request_without_access(self):
        other_user = User.objects.create_user(username='other_user', password='testpass123')
        self.client.login(username='other_user', password='testpass123')
        response = self.client.get(reverse('add_pull_request', args=[self.repository.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_add_pull_request_unauthenticated(self):
        response = self.client.get(reverse('add_pull_request', args=[self.repository.id]))
        self.assertEqual(response.status_code, 302)


class MergePullRequestViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.source_branch = Branch.objects.create(name='Source Branch', repository=cls.repository)
        cls.target_branch = Branch.objects.create(name='Target Branch', repository=cls.repository)
        cls.pull_request = PullRequest.objects.create(
            name='Example PR',
            repository=cls.repository,
            source=cls.source_branch,
            target=cls.target_branch,
            status=PullRequestStatus.OPEN.value
        )

    def test_merge_open_pull_request(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('merge_pull_request', args=[self.repository.id, self.pull_request.id]))
        self.pull_request.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.pull_request.status, PullRequestStatus.MERGED.value)
        self.assertRedirects(response, reverse('pull_request_detail', args=[self.repository.id, self.pull_request.id]))

    def test_merge_non_open_pull_request(self):
        self.client.login(username='user_with_access', password='testpass123')
        self.pull_request.status = PullRequestStatus.CLOSED.value
        self.pull_request.save()
        response = self.client.post(reverse('merge_pull_request', args=[self.repository.id, self.pull_request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Only open pull requests can be merged.', response.content.decode())

    def test_merge_pull_request_without_access(self):
        other_user = User.objects.create_user(username='other_user', password='testpass123')
        self.client.login(username='other_user', password='testpass123')
        response = self.client.post(reverse('merge_pull_request', args=[self.repository.id, self.pull_request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_merge_pull_request_unauthenticated(self):
        response = self.client.post(reverse('merge_pull_request', args=[self.repository.id, self.pull_request.id]))
        self.assertEqual(response.status_code, 302)

    def test_nonexistent_pull_request_merge(self):
        self.client.login(username='user_with_access', password='testpass123')
        response = self.client.post(reverse('merge_pull_request', args=[self.repository.id, 9999]))  # Non-existent PR ID
        self.assertEqual(response.status_code, 404)


class ApprovePullRequestViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_access = User.objects.create_user(username='user_with_access', password='testpass123')
        cls.reviewer_user = User.objects.create_user(username='reviewer_user', password='testpass123')
        cls.non_reviewer_user = User.objects.create_user(username='non_reviewer_user', password='testpass123')

        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user_with_access, public=False)
        cls.repository.collaborators.add(cls.reviewer_user, cls.non_reviewer_user)

        cls.source_branch = Branch.objects.create(name='Source Branch', repository=cls.repository)
        cls.target_branch = Branch.objects.create(name='Target Branch', repository=cls.repository)
        cls.pull_request = PullRequest.objects.create(
            name='Example PR',
            repository=cls.repository,
            source=cls.source_branch,
            target=cls.target_branch,
            status=PullRequestStatus.OPEN.value
        )
        cls.pull_request.reviewers.add(cls.reviewer_user)

    def test_approve_open_pull_request_by_reviewer(self):
        self.client.login(username='reviewer_user', password='testpass123')
        response = self.client.post(reverse('approve_pull_request', args=[self.repository.id, self.pull_request.id]))
        self.pull_request.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.pull_request.reviewed)
        self.assertRedirects(response, reverse('pull_request_detail', args=[self.repository.id, self.pull_request.id]))

    def test_approve_pull_request_non_reviewer(self):
        self.client.login(username='non_reviewer_user', password='testpass123')
        response = self.client.post(reverse('approve_pull_request', args=[self.repository.id, self.pull_request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You are not authorized to approve this pull request.', response.content.decode())

    def test_approve_non_open_pull_request(self):
        self.client.login(username='reviewer_user', password='testpass123')
        self.pull_request.status = PullRequestStatus.CLOSED.value
        self.pull_request.save()
        response = self.client.post(reverse('approve_pull_request', args=[self.repository.id, self.pull_request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('This pull request cannot be approved as it is not open.', response.content.decode())

    def test_approve_pull_request_without_access(self):
        other_user = User.objects.create_user(username='other_user', password='testpass123')
        self.client.login(username='other_user', password='testpass123')
        response = self.client.post(reverse('approve_pull_request', args=[self.repository.id, self.pull_request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_approve_pull_request_unauthenticated(self):
        response = self.client.post(reverse('approve_pull_request', args=[self.repository.id, self.pull_request.id]))
        self.assertEqual(response.status_code, 302)

    def test_nonexistent_pull_request_approval(self):
        self.client.login(username='reviewer_user', password='testpass123')
        response = self.client.post(reverse('approve_pull_request', args=[self.repository.id, 9999]))  # Non-existent PR ID
        self.assertEqual(response.status_code, 404)
