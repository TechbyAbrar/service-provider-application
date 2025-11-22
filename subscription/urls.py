from django.urls import path
from .views import (
    SubscriptionPlanAPIView,
    CheckoutSessionAPIView,
    UserSubscriptionAPIView,
    StripeWebhookAPIView,
)

urlpatterns = [
    path("plans/", SubscriptionPlanAPIView.as_view(), name="plans"),
    path("checkout/", CheckoutSessionAPIView.as_view(), name="checkout"),
    path("me/subscriptions/", UserSubscriptionAPIView.as_view(), name="user-subscriptions"),
    path("stripe/webhook/", StripeWebhookAPIView.as_view(), name="stripe-webhook"),
]
