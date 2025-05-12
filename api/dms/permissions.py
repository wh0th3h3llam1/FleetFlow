from rest_framework import permissions

from dms.models import Driver


class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        return Driver.objects.filter(user=request.user, is_active=True).exists()
