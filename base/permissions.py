from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):
        if (
            request.method in SAFE_METHODS and request.user.is_authenticated
        ) or request.user.is_staff:
            return True
        return False
