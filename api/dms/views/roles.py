from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Role
from core.serializers import RoleSerializer


class RoleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RoleSerializer

    def get_queryset(self):
        return Role.objects.prefetch_related("users").filter(is_system_defined=False)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_deletable:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"error": "Unable to delete the role as it is assigned to users."},
            )
