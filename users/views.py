from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.serializers import ManageUserSerializer, UserSerializer


class CreateUserView(generics.CreateAPIView):
    """
    API endpoint for user registration.

    - Allows anyone to create a new user account.
    - Uses `UserSerializer` to validate and save user data.
    - Accessible without authentication.
    """

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating the authenticated user's profile.

    - `GET`: Returns current user's profile using `UserSerializer`.
    - `PUT` / `PATCH`: Updates profile using `ManageUserSerializer`, which supports password change.
    - Requires authentication.
    - Automatically targets `request.user` as the object.
    """

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ManageUserSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user
