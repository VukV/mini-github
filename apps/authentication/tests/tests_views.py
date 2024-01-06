from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from apps.authentication.forms import ProfileUpdateForm


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


class MyProfileViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')

    def setUp(self):
        self.client.login(username='testuser', password='testpass123')

    def test_profile_view_get(self):
        response = self.client.get(reverse('my_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/my_profile.html')
        self.assertIsInstance(response.context['form'], ProfileUpdateForm)

    def test_profile_update_valid_post(self):
        form_data = {'username': 'updateduser', 'email': 'updated@example.com'}
        response = self.client.post(reverse('my_profile'), form_data)
        self.assertRedirects(response, reverse('my_profile'))
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.username, 'updateduser')
        self.assertEqual(updated_user.email, 'updated@example.com')

    def test_profile_update_invalid_post(self):
        form_data = {'username': '', 'email': 'invalid-email'}
        response = self.client.post(reverse('my_profile'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'This field is required.')
        self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')

    def test_profile_view_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(reverse('my_profile'))
        self.assertNotEqual(response.status_code, 200)
