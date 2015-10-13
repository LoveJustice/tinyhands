from rest_framework import permissions


class HasPermission(permissions.BasePermission):
    message = 'You do not have the right permission to access this data'

    def has_permission(self, request, view):
        for permission_str in view.permissions_required:
            if not getattr(request.user, permission_str):
                return False
        return True
