from django.test import TestCase

from apps.branch.forms import BranchForm


class BranchFormTest(TestCase):

    def test_branch_form_valid_data(self):
        form_data = {
            'name': 'New Branch'
        }
        form = BranchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_branch_form_invalid_data(self):
        form_data = {
            'name': ''
        }
        form = BranchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('This field is required.', form.errors['name'])
