from rest_framework import serializers

from common.constants import PermissionModels
from core.serializers import DynamicFieldsModelSerializer
from users.models import User
from users.serializers import PermissionSerializer


class ProfileSerializer(DynamicFieldsModelSerializer):

    role_name = serializers.CharField(source="role.role_name", read_only=True)
    permissions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "contact_number",
            "role_name",
            "permissions",
        )
        read_only_fields = ("username",)

    def get_permissions(self, instance):
        permissions_models = PermissionModels.all()

        perms = PermissionSerializer(
            instance.user_permissions.filter(content_type__model__in=permissions_models),
            many=True,
            fields=["codename"],
        ).data
        all_perms = {}
        for model in permissions_models:
            all_perms[model] = {"add": False, "change": False, "delete": False, "view": False}
        for perm in perms:
            p = perm["codename"].split("_")
            action, model = p[0], p[1]
            if action in all_perms[model]:
                all_perms[model][action] = True

        return all_perms
