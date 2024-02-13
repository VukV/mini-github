from django.test import TestCase
from apps.comment.forms import CommentForm


class CommentFormTest(TestCase):

    def test_valid_data(self):
        form = CommentForm(data={'text': 'This is a test comment'})
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = CommentForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)
