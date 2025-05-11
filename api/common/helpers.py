from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import Permission
from django.forms import ValidationError
from django.utils import timezone

from common.constants import SystemRoles


def create_system_roles():

    from users.models import Role

    all_permissions = Permission.objects.select_related("content_type").filter(
        content_type__app_label__in=settings.LOCAL_APPS
    )
    sys_admin, _ = Role.objects.get_or_create(
        role_name=SystemRoles.SYS_ADMIN, is_system_defined=True
    )
    _ = [sys_admin.permissions.add(perm) for perm in all_permissions]

    driver, _ = Role.objects.get_or_create(role_name=SystemRoles.DRIVER, is_system_defined=True)


def get_profile_image_path(instance, filename, **kwargs) -> str:
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid4(), ext)
    file_path = f"users/profile/{instance.username}_{filename}"
    return file_path


def get_order_attachment_path(instance, filename, **kwargs):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid4(), ext)
    file_path = f"order_attachments/{instance.attachment_type}_{filename}"
    return file_path


def no_past_date(value):
    today = timezone.now().date()
    if value < today:
        raise ValidationError("Date cannot be in the past.")
