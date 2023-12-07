from django.test import TestCase
from django.contrib.auth.models import User
from apps.repository.forms import RepositoryForm


class RepositoryFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_repository_form_valid_data(self):
        form = RepositoryForm(data={
            'name': 'Test Repository',
            'public': True
        })
        self.assertTrue(form.is_valid())

    def test_repository_form_invalid_data(self):
        form = RepositoryForm(data={
            'name': '',  # empty name should make the form invalid
            'public': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_repository_form_field_label(self):
        form = RepositoryForm()
        self.assertTrue(form.fields['name'].label is None or form.fields['name'].label == 'Name')
        self.assertTrue(form.fields['public'].label is None or form.fields['public'].label == 'Public')

    def test_repository_form_default_public_value(self):
        form = RepositoryForm()
        self.assertEqual(form.fields['public'].initial, True)
