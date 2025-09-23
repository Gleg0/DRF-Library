from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User


class UserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("users:create-user")
        self.token_url = reverse("users:token_obtain_pair")
        self.me_url = reverse("users:manage-user")

        self.user_data = {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_register_user(self):
        data = {
            "email": "new@example.com",
            "password": "bestpass",
            "first_name": "new",
            "last_name": "user"
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_login_user(self):
        response = self.client.post(self.token_url, {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.token = response.data["access"]

    def test_get_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_update_profile_with_password(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "current_password": self.user_data["password"],
            "new_password": "bestpassupdate"
        }
        response = self.client.put(self.me_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("bestpassupdate"))

    def test_update_profile_wrong_current_password(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "test",
            "new_password": "bestpasssss"
        }
        response = self.client.put(self.me_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("current_password", response.data)
