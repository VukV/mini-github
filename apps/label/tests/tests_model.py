from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from apps.label.models import Label
from apps.repository.models import Repository


class LabelModelTest(TestCase):

    def test_label_creation(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        repository = Repository.objects.create(name='Test Repository', owner=user)

        label = Label.objects.create(
            name='Test Label',
            description='This is a test label',
            color='#00FF00',
            repository=repository
        )

        self.assertEqual(label.name, 'Test Label')
        self.assertEqual(label.description, 'This is a test label')
        self.assertEqual(label.color, '#00FF00')
        self.assertEqual(label.repository, repository)

    def test_label_str_representation(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        repository = Repository.objects.create(name='Test Repository', owner=user)
        label = Label.objects.create(
            name='Test Label',
            description='This is a test label',
            color='#00FF00',
            repository=repository
        )

        expected_str = 'Test Label'
        self.assertEqual(str(label), expected_str)

    def test_blank_fields(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        repository = Repository.objects.create(name='Test Repository', owner=user)
        label = Label.objects.create(repository=repository)

        self.assertEqual(label.name, '')
        self.assertEqual(label.description, '')

    def test_required_fields(self):
        with self.assertRaises(IntegrityError):
            Label.objects.create(name='Test Label', description='This is a test label', color='#00FF00')
