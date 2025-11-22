from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stripe_price_id", "created_at")
    search_fields = ("name", "stripe_price_id")
    ordering = ("price",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "active", "start_date", "end_date", "stripe_subscription_id")
    list_filter = ("active", "plan")
    search_fields = ("user__email", "stripe_subscription_id")
    ordering = ("-start_date",)
    readonly_fields = ("created_at",)
