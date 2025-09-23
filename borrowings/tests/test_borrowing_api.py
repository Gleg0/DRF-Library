import datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingAdminDetailSerializer,
    BorrowingAdminListSerializer,
    BorrowingDetailSerializer,
    BorrowingListSerializer,
)

BORROWINGS_URL = reverse("borrowings:borrowing-list")


def detail_url(borrowing_id):
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


def return_url(borrowing_id):
    return reverse(
        "borrowings:borrowing-borrowing-return", args=[borrowing_id]
    )


def sample_book(**params):
    defaults = {
        "title": "Kobzar",
        "author": "Taras Shevchenko",
        "cover": "HARD",
        "inventory": 5,
        "daily_fee": 2.00,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(user, **params):
    book = params.pop("book", None)
    if book is None:
        book = sample_book()

    defaults = {
        "borrow_date": datetime.date(2025, 9, 23),
        "expected_return": datetime.date(2025, 9, 25),
        "book": book,
        "user": user,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpassword123"
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book()
        self.custom_book = sample_book(
            title="Way of the Wolf",
            author="Jordan Belfort",
            cover="HARD",
            inventory=2,
            daily_fee=5.00,
        )
        self.borrowing = sample_borrowing(self.user)
        self.custom_borrowing = sample_borrowing(
            user=self.user,
            borrow_date=datetime.date(2025, 9, 23),
            expected_return=datetime.date(2025, 9, 28),
            book=self.custom_book,
        )

    def test_borrowing_list(self):
        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)
        res = self.client.get(BORROWINGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_borrowings_by_is_active_status(self):
        self.custom_borrowing.actual_return_date = datetime.date(2025, 9, 27)
        self.custom_borrowing.save()

        res = self.client.get(BORROWINGS_URL, {"actual_return_date": "True"})

        serializer_sample_borrowing = BorrowingListSerializer(self.borrowing)
        serializer_custom_borrowing = BorrowingListSerializer(
            self.custom_borrowing
        )

        self.assertIn(serializer_sample_borrowing.data, res.data["results"])
        self.assertNotIn(serializer_custom_borrowing.data, res.data["results"])

    def test_retrieve_borrowing_detail(self):
        url = detail_url(self.borrowing.id)

        res = self.client.get(url)

        serializer = BorrowingDetailSerializer(self.borrowing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self):
        initial_inventory = self.custom_book.inventory
        payload = {
            "borrow_date": "2025-09-23",
            "expected_return": "2025-09-25",
            "book": self.custom_book.id,
        }

        res = self.client.post(BORROWINGS_URL, payload, format="json")
        self.custom_book.refresh_from_db()
        borrowing = Borrowing.objects.get(id=res.data["id"])
        self.assertEqual(self.custom_book.inventory, initial_inventory - 1)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(borrowing.user, self.user)

    def test_create_borrowing_book_not_available(self):
        book = self.custom_book
        book.inventory = 0
        book.save()

        payload = {
            "borrow_date": "2025-09-23",
            "expected_return": "2025-09-25",
            "book": book.id,
        }
        res = self.client.post(BORROWINGS_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_borrowing(self):
        borrowing = self.borrowing
        book = borrowing.book
        initial_inventory = book.inventory

        url = return_url(self.borrowing.id)

        payload = {}
        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        borrowing.refresh_from_db()
        book.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)
        self.assertEqual(book.inventory, initial_inventory + 1)

    def test_repeated_return_borrowing(self):
        borrowing = self.borrowing
        borrowing.actual_return_date = datetime.date(2025, 9, 24)
        borrowing.save()

        url = return_url(self.borrowing.id)

        payload = {}
        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class AdminBorrowingTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            email="admin@test.com", password="testpassword123", is_staff=True
        )
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpassword123"
        )
        self.client.force_authenticate(self.admin_user)
        self.borrowing = sample_borrowing(self.user)
        self.custom_borrowing = sample_borrowing(self.admin_user)
        self.custom_book = sample_book(
            title="Way of the Wolf",
            author="Jordan Belfort",
            cover="HARD",
            inventory=2,
            daily_fee=5.00,
        )

    def test_admin_borrowing_list(self):
        borrowings = Borrowing.objects.all()
        serializer = BorrowingAdminListSerializer(borrowings, many=True)
        res = self.client.get(BORROWINGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_admin_retrieve_borrowing_detail(self):
        url = detail_url(self.borrowing.id)

        res = self.client.get(url)

        serializer = BorrowingAdminDetailSerializer(self.borrowing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_admin_update_borrowing(self):
        borrowing = self.borrowing

        url = detail_url(self.borrowing.id)
        payload = {
            "expected_return": "2025-09-30",
        }
        res = self.client.patch(url, payload, format="json")
        borrowing.refresh_from_db()
        self.custom_book.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(borrowing.expected_return), payload["expected_return"]
        )
