from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class LoginViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='testuser', password='testpass123')

    def test_login_page_load(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

    def test_valid_login(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass123'})
        user = authenticate(username='testuser', password='testpass123')
        self.assertIsNotNone(user)
        self.assertRedirects(response, '/')

    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {'username': 'wronguser', 'password': 'wrongpass'})
        self.assertTemplateUsed(response, 'auth/login.html')
        self.assertIn('Invalid username or password', response.context['error_message'])


class RegisterViewTests(TestCase):

    def test_register_page_load(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/register.html')

    def test_valid_registration(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(reverse('register'), form_data)
        self.assertRedirects(response, '/')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_invalid_registration(self):
        form_data = {
            'username': '',
            'email': 'user@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(reverse('register'), form_data)
        self.assertTemplateUsed(response, 'auth/register.html')
        self.assertIn('This field is required.', response.context['error_message'])


class LogoutViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='testuser', password='testpass123')

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        response = self.client.get(reverse('login'))
        self.assertFalse(response.context['user'].is_authenticated)
