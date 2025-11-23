from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth import get_user_model
from subscription.models import UserSubscription

from django.db import models

User = get_user_model()

# Cache keys
TOTAL_USERS_CACHE_KEY = "dashboard_total_users"
TOTAL_EARNINGS_CACHE_KEY = "dashboard_total_earnings"
TOTAL_VERIFIED_CACHE_KEY = "dashboard_total_verified"
TOTAL_UNVERIFIED_CACHE_KEY = "dashboard_total_unverified"

# Functions to update cache
def update_total_users_cache():
    cache.set(TOTAL_USERS_CACHE_KEY, User.objects.count(), 60)

def update_total_earnings_cache():
    total = UserSubscription.objects.filter(active=True).aggregate(total=models.Sum("plan__price"))["total"] or 0
    cache.set(TOTAL_EARNINGS_CACHE_KEY, total, 60)

def update_total_verified_cache():
    verified_count = User.objects.filter(is_verified=True).count()
    cache.set(TOTAL_VERIFIED_CACHE_KEY, verified_count, 60)
    unverified_count = User.objects.filter(is_verified=False).count()
    cache.set(TOTAL_UNVERIFIED_CACHE_KEY, unverified_count, 60)

# Signals
@receiver(post_save, sender=User)
@receiver(post_delete, sender=User)
def refresh_user_caches(sender, instance, **kwargs):
    update_total_users_cache()
    update_total_verified_cache()

@receiver(post_save, sender=UserSubscription)
@receiver(post_delete, sender=UserSubscription)
def refresh_subscription_caches(sender, instance, **kwargs):
    update_total_earnings_cache()
