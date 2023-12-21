from django.test import TestCase
from apps.commit.forms import CommitForm


class CommitFormTest(TestCase):

    def test_commit_form_valid_data(self):
        form_data = {
            'message': 'Initial commit'
        }
        form = CommitForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_commit_form_invalid_data(self):
        form_data = {
            'message': ''
        }
        form = CommitForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
        self.assertIn('This field is required.', form.errors['message'])
