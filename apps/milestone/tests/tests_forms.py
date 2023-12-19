from django.test import TestCase
from datetime import date

from apps.milestone.forms import MilestoneForm


class MilestoneFormTest(TestCase):

    def test_milestone_form_valid_data(self):
        form_data = {
            'name': 'Release v1.0',
            'description': 'First major release.',
            'date_due': date.today().isoformat()
        }
        form = MilestoneForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_milestone_form_invalid_data(self):
        form_data = {
            'name': '',
            'description': '',
            'date_due': 'invalid-date'
        }
        form = MilestoneForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('date_due', form.errors)

    def test_milestone_form_missing_field(self):
        form_data = {
            'name': 'Release v1.0',
            'description': 'First major release.'
        }
        form = MilestoneForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_due', form.errors)
