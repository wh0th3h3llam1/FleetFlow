from __future__ import annotations
from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.utils.functional import cached_property
from django.utils.text import slugify

from django_lifecycle import BEFORE_CREATE, BEFORE_UPDATE, LifecycleModelMixin, hook
from phonenumber_field.modelfields import PhoneNumberField

from common.helpers import get_profile_image_path
from core.models import BaseModel
from users.managers import UserManager

if TYPE_CHECKING:
    from django.db.models import Manager

# Create your models here.


class Role(LifecycleModelMixin, BaseModel):
    role_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=500)
    is_system_defined = models.BooleanField(default=False)
    permissions = models.ManyToManyField(
        to=Permission,
        verbose_name="Role Permissions",
        blank=True,
        help_text="Specific permissions for this role.",
        related_name="roles",
    )

    @hook(BEFORE_UPDATE, when="role_name", has_changed=True)
    @hook(BEFORE_CREATE)
    def do_after_create_jobs(self):
        self.slug = slugify(self.role_name)

    def no_of_users(self):
        if self.users:
            return self.users.count()
        return 0

    @cached_property
    def is_deletable(self):
        return not self.users.count()

    def __str__(self) -> str:
        return f"{self.role_name}"


class User(BaseModel, AbstractUser):

    role = models.ForeignKey(
        to=Role,
        related_name="users",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    contact_number = PhoneNumberField(
        verbose_name="Contact Number",
        blank=True,
        null=True,
    )
    profile_image = models.FileField(upload_to=get_profile_image_path, blank=True, null=True)
    deactivated_on = models.DateTimeField(verbose_name="Deactivated On", blank=True, null=True)
    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return f"{self.username or self.email or self.id}"

    def clean(self) -> None:
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def full_name(self):
        return f"{self.first_name} - {self.last_name}"

    @cached_property
    def projects_with_access(self):
        return list(self.user_projects.values_list("project__project_id", flat=True))
