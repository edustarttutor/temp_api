from rest_framework.permissions import BasePermission, SAFE_METHODS


class LimitedPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS and request.user.is_superuser == False:
            return False
        return True
        

