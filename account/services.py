from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models

from .signals import (
    TOTAL_USERS_CACHE_KEY,
    TOTAL_EARNINGS_CACHE_KEY,
    TOTAL_VERIFIED_CACHE_KEY,
    TOTAL_UNVERIFIED_CACHE_KEY
)

User = get_user_model()

class DashboardService:
    @staticmethod
    def get_total_users():
        return cache.get(TOTAL_USERS_CACHE_KEY) or User.objects.count()

    @staticmethod
    def get_total_earnings():
        from subscription.models import UserSubscription
        return cache.get(TOTAL_EARNINGS_CACHE_KEY) or UserSubscription.objects.filter(active=True).aggregate(total=models.Sum("plan__price"))["total"] or 0

    @staticmethod
    def get_total_verified():
        return cache.get(TOTAL_VERIFIED_CACHE_KEY) or User.objects.filter(is_verified=True).count()

    @staticmethod
    def get_total_unverified():
        return cache.get(TOTAL_UNVERIFIED_CACHE_KEY) or User.objects.filter(is_verified=False).count()

    @staticmethod
    def get_users_queryset():
        return User.objects.all().order_by("-created_at")

    @staticmethod
    def get_user_by_id(user_id):
        return User.objects.prefetch_related("subscriptions__plan").filter(user_id=user_id).first()
    
    
    
# social auth
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()

@transaction.atomic
def social_login(provider: str, data: dict) -> User:
    """
    Create or update a user from social login.
    Accepts minimal info if some fields missing.
    """
    email = data.get("email")
    if not email:
        raise ValueError(f"{provider} did not return an email")

    full_name = data.get("full_name") or email.split("@")[0]
    profile_pic_url = data.get("profile_pic_url")

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "full_name": full_name,
            "username": email.split("@")[0],
            "profile_pic_url": profile_pic_url
        }
    )

    # Update profile picture if changed
    if profile_pic_url and user.profile_pic_url != profile_pic_url:
        user.profile_pic_url = profile_pic_url
        user.save(update_fields=["profile_pic_url"])

    return user
