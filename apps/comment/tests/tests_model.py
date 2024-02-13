from django.contrib.auth.models import User
from django.test import TestCase

from apps.branch.models import Branch
from apps.comment.models import Comment
from apps.pull_request.models import PullRequest
from apps.repository.models import Repository


class CommentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.repository = Repository.objects.create(name="Test Repo", public=True, owner=cls.user)
        cls.branch = Branch.objects.create(name="main", default=True, repository=cls.repository)
        cls.pull_request = PullRequest.objects.create(
            name="Test PR",
            source=cls.branch,
            target=cls.branch,
            author=cls.user,
            repository=cls.repository
        )

    def test_create_comment(self):
        comment = Comment.objects.create(
            author=self.user,
            text="This is a test comment",
            pull_request=self.pull_request
        )
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.text, "This is a test comment")
        self.assertEqual(comment.pull_request, self.pull_request)
        self.assertIsNone(comment.replied_to)
        self.assertFalse(comment.is_reply())

    def test_create_reply_to_comment(self):
        parent_comment = Comment.objects.create(
            author=self.user,
            text="Parent comment",
            pull_request=self.pull_request
        )
        reply_comment = Comment.objects.create(
            author=self.user,
            text="Reply to comment",
            pull_request=self.pull_request,
            replied_to=parent_comment
        )
        self.assertEqual(reply_comment.replied_to, parent_comment)
        self.assertTrue(reply_comment.is_reply())
