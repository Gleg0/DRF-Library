from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer


from rest_framework import viewsets


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
