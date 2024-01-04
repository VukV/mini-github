from django import forms
from django.contrib.auth.models import User
from django.test import TestCase
from apps.authentication.forms import LoginForm, RegisterForm, ProfileUpdateForm


class LoginFormTest(TestCase):

    def test_form_fields(self):
        form = LoginForm()
        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)

    def test_password_field_widget(self):
        form = LoginForm()
        self.assertIsInstance(form.fields['password'].widget, forms.PasswordInput)

    def test_valid_form(self):
        form_data = {'username': 'testuser', 'password': 'testpass123'}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {'username': '', 'password': ''}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)


class RegisterFormTest(TestCase):

    def test_form_fields(self):
        form = RegisterForm()
        expected_fields = ['username', 'email', 'password1', 'password2']
        for field in expected_fields:
            self.assertIn(field, form.fields)

    def test_email_field_properties(self):
        form = RegisterForm()
        self.assertIsInstance(form.fields['email'], forms.EmailField)

    def test_valid_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpass123',
            'password2': 'wrongpass'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class ProfileUpdateFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='existing_user', email='existing@example.com', password='testpass123')

    def test_profile_update_form_valid(self):
        form_data = {'username': 'newuser', 'email': 'newuser@example.com'}
        form = ProfileUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_profile_update_form_invalid_email(self):
        form_data = {'username': 'newuser', 'email': 'invalid-email'}
        form = ProfileUpdateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_profile_update_form_unique_username(self):
        form_data = {'username': 'existing_user', 'email': 'newemail@example.com'}
        form = ProfileUpdateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
