from django.shortcuts import render

from base.permissions import IsAdminOrIfAuthenticatedReadOnly
from books.models import Book
from books.serializers import BookListSerializer, BookSerializer


from rest_framework import viewsets


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookSerializer
