"""Sanity checks for the custom user manager and authentication."""

from django.test import TestCase
from django.urls import reverse

from apps.auths.models import User


class UserTests(TestCase):
    def test_user_can_login_with_email(self):
        user = User.objects.create_user(
            email="STUDENT@example.com", first_name="Sam", last_name="Lee",
            password="strong-test-password-123",
        )
        self.assertEqual(user.email, "student@example.com")
        self.assertTrue(user.check_password("strong-test-password-123"))

    def test_registration(self):
        response = self.client.post(
            reverse("auth-register"),
            {
                "email": "learner@example.com",
                "password": "strong-test-password-123",
                "first_name": "Ada",
                "last_name": "Lovelace",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
