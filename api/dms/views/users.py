from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from common.constants import ProjectStatus
from dms.models import Project
from users.models import User, Role
from users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet, PermissionRequiredMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return (
            User.objects.prefetch_related("user_projects")
            .select_related("role")
            .filter(is_active=True, role__is_system_defined=False)
            .exclude(id=self.request.user.id)
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        roles = Role.objects.filter(is_system_defined=False)
        context["all_roles"] = roles
        context["all_projects"] = Project.objects.filter(
            status=ProjectStatus.ACTIVE, project_id__in=self.request.user.projects_with_access
        )
        return context

    def get_serializer(self, *args, **kwargs):
        exclude = []

        if self.action == "list":
            exclude.append("all_projects")

        if exclude:
            kwargs["exclude"] = exclude

        return super().get_serializer(*args, **kwargs)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.role = None
        instance.save()
