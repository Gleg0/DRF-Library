from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.serializers import ManageUserSerializer, UserSerializer


class CreateUserView(generics.CreateAPIView):

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class ManageUserView(generics.RetrieveUpdateAPIView):

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ManageUserSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user
