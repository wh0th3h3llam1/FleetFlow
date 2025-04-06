from django.contrib.auth.models import Permission

from rest_framework import serializers
from djoser.conf import settings


from core.serializers import DynamicFieldsModelSerializer
from common.constants import PermissionModels
from users.models import User, Role


class PermissionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Permission
        fields = ("id", "name", "codename")
        read_only_fields = ("id",)


class RoleSerializer(DynamicFieldsModelSerializer):
    permissions = serializers.SerializerMethodField()
    updated_permissions = serializers.ListField(write_only=True)
    all_permissions = serializers.SerializerMethodField()
    is_deletable = serializers.BooleanField(read_only=True)

    def get_permissions(self, obj):
        modules = PermissionModels.all()

        role_permissions = obj.permissions.filter(content_type__model__in=modules)
        permissions = [perm.codename for perm in role_permissions]
        return permissions

    def get_all_permissions(self, obj):
        modules = PermissionModels.all()

        all_permissions = Permission.objects.filter(content_type__model__in=modules)
        all_perm = [perm.codename for perm in all_permissions]
        return all_perm

    def validate_updated_permissions(self, permissions):
        modules = PermissionModels.all()

        all_permissions = Permission.objects.filter(content_type__model__in=modules)
        non_existent_perms = [
            perm for perm in permissions if not all_permissions.filter(codename=perm).exists()
        ]
        if not permissions:
            raise serializers.ValidationError(
                detail="No Permission provided. You should select atleast one permission",
                code="no_permissions_given",
            )
        if non_existent_perms:
            non_existent_perms = f",".join(non_existent_perms)
            raise serializers.ValidationError(
                detail=f"Invalid Permissions Provided : {non_existent_perms}", code="does_not_exist"
            )
        return all_permissions.filter(codename__in=permissions)

    class Meta:
        model = Role
        fields = (
            "id",
            "role_name",
            "permissions",
            "updated_permissions",
            "is_deletable",
            "all_permissions",
        )

    def create(self, validated_data):
        updated_permissions = validated_data.pop("updated_permissions")

        role = super().create(validated_data)

        if updated_permissions:
            role.permissions.set(updated_permissions)

        return role

    def update(self, instance, validated_data):
        updated_permissions = None
        try:
            updated_permissions = validated_data.pop("updated_permissions")
        except KeyError:
            pass

        role = super().update(instance, validated_data)

        if updated_permissions:
            role.permissions.set(updated_permissions, clear=True)
            updated_perms = role.permissions.all()
            role_users = role.users.all()
            for user in role_users:
                user.user_permissions.set(updated_perms)

            for user in role_users:
                try:
                    user.auth_token.delete()
                except User.auth_token.RelatedObjectDoesNotExist as rodne:
                    pass
                except TypeError as te:
                    pass

        return role


class UserSerializer(DynamicFieldsModelSerializer):
    password = serializers.CharField(required=False, write_only=True)
    permissions = PermissionSerializer(source="user_permissions", many=True, read_only=True)
    roles = serializers.SerializerMethodField()
    role_name = serializers.ReadOnlyField(source="role.role_name", allow_null=True)

    def get_roles(self, instance: User):
        if self.context.get("all_roles"):
            roles = self.context.get("all_roles")
        else:
            roles = Role.objects.filter(is_system_defined=False)
        return RoleSerializer(roles, many=True, fields=("id", "role_name")).data

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "email",
            "contact_number",
            "profile_image",
            "role",
            "permissions",
            "roles",
            "role_name",
            "is_active",
        )
        read_only_fields = ("id", "is_active")
        extra_kwargs = {"role": {"error_messages": {"does_not_exist": "Role does not exist."}}}

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")

        user = User.objects.create_user(username=username, password=password, **validated_data)

        return user

    def update(self, instance, validated_data):
        updated_password = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)

        if updated_password:
            instance.set_password(updated_password)
            instance.save()

        return instance


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source="key")

    user = UserSerializer(fields=("id", "username"))

    class Meta:
        model = settings.TOKEN_MODEL
        fields = ("token", "user")
