from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from common.admin_utils import FieldSets
from users.models import User

# Register your models here.


class UserAdmin(BaseUserAdmin):
    fieldsets = FieldSets(
        none=("username", "password"),
        personal_info=("email", "first_name", "last_name", "phone_number"),
        permissions=("is_active", "is_staff", "is_superuser", "groups"),
        important_dates=(
            "deactivated_on",
            "created",
            "last_login",
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "usable_password", "password1", "password2"),
            },
        ),
    )


admin.site.register(User, UserAdmin)
