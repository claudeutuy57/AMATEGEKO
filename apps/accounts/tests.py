from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser

class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_student_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newlearner',
            'first_name': 'Jean',
            'last_name': 'Mugabo',
            'email': 'jean@amategeko.rw',
            'phone_number': '0788999888',
            'preferred_language': 'rw',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)  # Redirects to dashboard
        user = CustomUser.objects.filter(username='newlearner').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.is_learner)
        self.assertEqual(user.phone_number, '0788999888')

    def test_user_login_and_logout(self):
        user = CustomUser.objects.create_user(
            username='authuser',
            password='MyPassword123!',
            email='auth@amategeko.rw'
        )
        # Login
        login_resp = self.client.post(reverse('accounts:login'), {
            'username': 'authuser',
            'password': 'MyPassword123!',
        })
        self.assertEqual(login_resp.status_code, 302)

        # Logout
        logout_resp = self.client.get(reverse('accounts:logout'))
        self.assertEqual(logout_resp.status_code, 302)

