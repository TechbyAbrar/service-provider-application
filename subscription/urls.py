from django.urls import path
from .views import (
    SubscriptionPlanAPIView,
    CheckoutSessionAPIView,
    UserSubscriptionAPIView,
    CancelSubscriptionAPIView,
    StripeWebhookAPIView,
)

urlpatterns = [
    path("plans/", SubscriptionPlanAPIView.as_view(), name="plans"),
    path("my/checkout/", CheckoutSessionAPIView.as_view(), name="checkout"),
    path("my/plan/", UserSubscriptionAPIView.as_view(), name="user-subscriptions"),
    path("cancel/my/subscription/", CancelSubscriptionAPIView.as_view(), name="cancel-subscription"),
    path("stripe/webhook/", StripeWebhookAPIView.as_view(), name="stripe-webhook"),
]
