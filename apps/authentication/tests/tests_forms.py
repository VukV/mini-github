from django import forms
from django.test import TestCase
from apps.authentication.forms import LoginForm, RegisterForm


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
