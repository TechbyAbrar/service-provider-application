from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Fields to display in the admin list view
    list_display = (
        "user_id",
        "email",
        "username",
        "full_name",
        "phone",
        "is_verified",
        "is_staff",
        "is_superuser",
        "created_at",
    )

    # Fields to filter by in the admin
    list_filter = ("is_verified", "is_staff", "is_superuser", "created_at")

    # Fields searchable in admin
    search_fields = ("email", "username", "full_name", "phone", "company_name")

    # Fields used when creating/updating a user in admin
    fieldsets = (
        (None, {"fields": ("email", "username", "full_name", "phone", "profile_pic", "profile_pic_url", "country")}),
        ("Verification", {"fields": ("otp", "otp_expired", "is_verified")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Company & Bank Info", {"fields": ("company_name", "cvr_number", "bank_name", "account_number", "iban", "swift_ibc")}),
        ("Financial", {"fields": ("hourly_rate", "profit_on_materials", "risk_margin")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = ("created_at", "updated_at")

    ordering = ("-created_at",)
