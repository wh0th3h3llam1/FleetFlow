from django import forms
from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _

from .models import DashUser as CustomUser
from .models import Role


class DashUserCreationForm(UserCreationForm):
    
    role = forms.ModelChoiceField(queryset=Role.objects.all())

    class Meta:
        model = CustomUser
        fields = ('email', "username", 'role')


class DashUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email',)
        readonly_fields = ("user_permissions")


class RoleAdminForm(forms.ModelForm):
    
    class Meta:
        model = Role
        fields = ("role_name", "is_system_defined", "permissions")

    # slug = forms.CharField(read)
    permissions = forms.ModelMultipleChoiceField(
        Permission.objects.exclude(content_type__app_label__in=['auth', "sessions", "contenttypes", "admin"]), 
        widget=admin.widgets.FilteredSelectMultiple(_('permissions'), False))

