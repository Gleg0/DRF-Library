from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from base.permissions import IsAdminOrIfAuthenticatedReadOnly
from books.models import Book
from books.serializers import BookListSerializer, BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookSerializer

    def get_permissions(self):
        if self.action == "list":
            return (AllowAny,)
        return (IsAdminOrIfAuthenticatedReadOnly,)