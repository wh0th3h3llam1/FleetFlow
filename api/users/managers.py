from django.apps import apps
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

from common.constants import SystemRoles
from common.helpers import create_system_roles


class UserManager(BaseUserManager):
    """
    User model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, username, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """

        if not username:
            raise ValueError(_("The Username must be set"))

        email = extra_fields.get("email")
        if email:
            email = self.normalize_email(email)
            extra_fields["email"] = email

        role = extra_fields.get("role")
        if role and isinstance(role, int):
            Role = apps.get_model("users", "Role")
            extra_fields["role"] = Role.objects.get(id=role)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        Role = apps.get_model("users", "Role")

        if "role" not in extra_fields:
            create_system_roles()
            role = Role.objects.get(role_name=SystemRoles.SYS_ADMIN, is_system_defined=True)
            extra_fields["role"] = role
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, password, **extra_fields)
