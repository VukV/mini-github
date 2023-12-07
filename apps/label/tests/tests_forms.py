from django.test import TestCase
from apps.label.forms import LabelForm, validate_hex_color


class LabelFormTest(TestCase):

    def test_form_fields(self):
        form = LabelForm()
        expected_fields = ['name', 'description', 'color']
        for field in expected_fields:
            self.assertIn(field, form.fields)

    def test_valid_form(self):
        form_data = {
            'name': 'Test Label',
            'description': 'This is a test label',
            'color': '#00FF00'
        }
        form = LabelForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'name': 'Invalid Label',
            'description': 'This label has an invalid color',
            'color': 'invalid_color'
        }
        form = LabelForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('color', form.errors)

    def test_empty_form(self):
        form_data = {}
        form = LabelForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('color', form.errors)
