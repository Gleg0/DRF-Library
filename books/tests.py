from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book

User = get_user_model()


class BookViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse("books:book-list")
        self.user = User.objects.create_user(
            email="user@user.com", password="pass"
        )
        self.admin = User.objects.create_superuser(
            email="admin@admin.com", password="adminpass"
        )

        Book.objects.create(
            title="Test book", author="Test", inventory=5, daily_fee=5
        )

    def test_public_list_books(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

    def test_auth_user_can_retrieve_book(self):
        self.client.force_authenticate(user=self.user)
        book = Book.objects.first()
        url = reverse("books:book-detail", args=[book.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], book.title)

    def test_admin_can_create_book(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "title": "Test book",
            "author": "Test",
            "cover": "HARD",
            "inventory": 3,
            "daily_fee": 2.00,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(title="Test book").exists())

    def test_not_admin_cannot_create_book(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Test book",
            "author": "Test",
            "inventory": 1,
            "daily_fee": 1.0,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
