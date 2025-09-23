from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.serializers import ManageUserSerializer, UserSerializer


@extend_schema(
    description="""
    API endpoint for user registration.

    - Allows anyone to create a new user account.
    - Uses `UserSerializer` to validate and save user data.
    - Accessible without authentication.
    """
)
class CreateUserView(generics.CreateAPIView):

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


@extend_schema(
    description="""
    API endpoint for retrieving and updating the authenticated user's profile.

    - `GET`: Returns current user's profile using `UserSerializer`.

    - `PUT` / `PATCH`: Updates profile using `ManageUserSerializer`,
      which supports password change.

    - Requires authentication.

    - Automatically targets `request.user` as the object.
    """
)
class ManageUserView(generics.RetrieveUpdateAPIView):

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ManageUserSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user
