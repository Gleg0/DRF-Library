import unittest
from rest_framework.test import APIRequestFactory

from payments.views import PaymentListRetrieveViewSet
from payments.serializers import PaymentListSerializer, PaymentDetailSerializer


factory = APIRequestFactory()


class PaymentViewSetSerializerTestCase(unittest.TestCase):
    def test_get_serializer_class_list(self):
        view = PaymentListRetrieveViewSet()
        view.action = "list"
        self.assertIs(view.get_serializer_class(), PaymentListSerializer)

    def test_get_serializer_class_detail(self):
        view = PaymentListRetrieveViewSet()
        view.action = "retrieve"
        self.assertIs(view.get_serializer_class(), PaymentDetailSerializer)
