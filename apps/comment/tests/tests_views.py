from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from apps.branch.models import Branch
from apps.comment.models import Comment
from apps.pull_request.models import PullRequest, PullRequestStatus
from apps.repository.models import Repository


class AddCommentViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        cls.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        cls.repository = Repository.objects.create(name='Test Repo', owner=cls.user, public=False)

        cls.source_branch = Branch.objects.create(name='Source Branch', repository=cls.repository)
        cls.target_branch = Branch.objects.create(name='Target Branch', repository=cls.repository)

        cls.pull_request = PullRequest.objects.create(name='Open PR', repository=cls.repository, status=PullRequestStatus.OPEN.value,
                                   source=cls.source_branch, target=cls.target_branch)

    def setUp(self):
        self.client.login(username='testuser', password='testpass123')

    def test_add_comment_valid_post(self):
        comment_data = {'text': 'Test comment'}
        response = self.client.post(reverse('add_comment', args=[self.pull_request.id]), comment_data)
        self.assertRedirects(response, reverse('pull_request_detail', args=[self.repository.id, self.pull_request.id]))
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().text, 'Test comment')

    def test_add_comment_invalid_post(self):
        response = self.client.post(reverse('add_comment', args=[self.pull_request.id]), {'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Comment text is required.', response.content.decode())

    def test_add_comment_unauthenticated_access(self):
        self.client.logout()
        comment_data = {'text': 'Test comment'}
        response = self.client.post(reverse('add_comment', args=[self.pull_request.id]), comment_data)
        self.assertNotEqual(response.status_code, 200)

    def test_add_comment_no_access(self):
        self.client.logout()
        self.client.login(username='otheruser', password='testpass123')
        comment_data = {'text': 'Test comment'}
        response = self.client.post(reverse('add_comment', args=[self.pull_request.id]), comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('You do not have access to this repository.', response.content.decode())

    def test_add_comment_nonexistent_pull_request(self):
        comment_data = {'text': 'Test comment'}
        response = self.client.post(reverse('add_comment', args=[9999]), comment_data)  # Non-existent PR ID
        self.assertEqual(response.status_code, 404)

