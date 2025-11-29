from django.urls import path
from .views import (
    SubscriptionPlanAPIView,
    CheckoutSessionAPIView,
    UserSubscriptionAPIView,
    CancelSubscriptionAPIView,
    StripeWebhookAPIView, EarnListAPIView, SubscriptionPlanDetailAPIView, SubscriptionPlanUpdateDeleteAPIView
)

urlpatterns = [
    path("plans/", SubscriptionPlanAPIView.as_view(), name="plans"),
    path("plans/<int:plan_id>/", SubscriptionPlanDetailAPIView.as_view(), name="plans"),
    path(
        "plans/<int:plan_id>/edit/", SubscriptionPlanUpdateDeleteAPIView.as_view(), name="subscription-plan-update-delete"
    ),
    path("my/checkout/", CheckoutSessionAPIView.as_view(), name="checkout"),
    path("my/plan/", UserSubscriptionAPIView.as_view(), name="user-subscriptions"),
    path("cancel/my/subscription/", CancelSubscriptionAPIView.as_view(), name="cancel-subscription"),
    path("stripe/webhook/", StripeWebhookAPIView.as_view(), name="stripe-webhook"),
    
    # admin earning
    path("admin/earnings/", EarnListAPIView.as_view(), name="earnings-list"),
]
