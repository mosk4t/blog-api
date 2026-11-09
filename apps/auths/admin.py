"""Unfold-powered admin for the custom email-based user model."""

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import BooleanRadioFilter
from unfold.decorators import action, display
from unfold.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)

from apps.auths.models import User


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name")

    def clean_email(self) -> str:
        return self.cleaned_data["email"].lower()


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm
    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name")
    list_display = ("identity", "active_badge", "staff_badge", "post_count")
    list_filter = (
        ("is_active", BooleanRadioFilter),
        ("is_staff", BooleanRadioFilter),
    )
    actions = ["activate_users", "deactivate_users"]
    readonly_fields = ("last_login", "date_joined")
    fieldsets = (
        ("Personal info", {"classes": ["tab"], "fields": ("email", "first_name", "last_name", "password")}),
        ("Permissions", {"classes": ["tab"], "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"classes": ["tab"], "fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "first_name", "last_name", "password1", "password2")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_post_count=Count("posts"))

    @display(description="User", header=True, ordering="email")
    def identity(self, obj: User) -> tuple[str, str, str]:
        initials = f"{obj.first_name[:1]}{obj.last_name[:1]}".upper()
        return obj.get_full_name(), obj.email, initials

    @display(description="Active", label={"yes": "success", "no": "danger"})
    def active_badge(self, obj: User) -> tuple[str, str]:
        return ("yes", "Active") if obj.is_active else ("no", "Inactive")

    @display(description="Staff", label={"yes": "info", "no": "warning"})
    def staff_badge(self, obj: User) -> tuple[str, str]:
        return ("yes", "Staff") if obj.is_staff else ("no", "Regular")

    @display(description="Posts", ordering="_post_count")
    def post_count(self, obj: User) -> int:
        return obj._post_count

    @action(description="Activate selected users")
    def activate_users(self, request, queryset) -> None:
        changed = queryset.update(is_active=True)
        self.message_user(request, f"Activated {changed} users")

    @action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset) -> None:
        changed = queryset.exclude(is_superuser=True).update(is_active=False)
        self.message_user(request, f"Deactivated {changed} users (superusers excluded)")


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    search_fields = ("name",)
