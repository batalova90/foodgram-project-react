from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if (request.user.is_authenticated
                or request.method in SAFE_METHODS):
            return True

    def has_object_permission(self, request, view, obj):
        if (obj.author == request.user
                or request.method in SAFE_METHODS):
            return True
