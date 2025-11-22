import logging
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import SubscriptionPlan, UserSubscription
from .serializers import (
    SubscriptionPlanSerializer,
    CheckoutSessionSerializer,
    UserSubscriptionSerializer,
)
from .services import StripeService

logger = logging.getLogger(__name__)


class PlanPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


# ============================
#   SUBSCRIPTION PLAN CRUD
# ============================

class SubscriptionPlanAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class = PlanPagination

    def get(self, request):
        paginator = self.pagination_class()
        plans = SubscriptionPlan.objects.all().order_by("price")
        page = paginator.paginate_queryset(plans, request)

        serializer = SubscriptionPlanSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Admin only."}, status=403)

        serializer = SubscriptionPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                # create plan
                plan = serializer.save()

                # create Stripe objects
                StripeService.create_stripe_product(plan)

            return Response(
                SubscriptionPlanSerializer(plan).data,
                status=201
            )

        except Exception as e:
            logger.exception("[Plan] Failed to create plan")
            return Response(
                {"detail": str(e)},
                status=500
            )


# ============================
#   CHECKOUT SESSION API
# ============================

class CheckoutSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan = get_object_or_404(SubscriptionPlan, id=serializer.validated_data["plan_id"])

        try:
            with transaction.atomic():

                price_id = StripeService.create_stripe_product(plan)

                current_sub = UserSubscription.objects.filter(
                    user=request.user,
                    active=True
                ).first()

                metadata = {"user_id": request.user.user_id, "plan_id": plan.id}

                if current_sub:
                    metadata["current_subscription_id"] = current_sub.stripe_subscription_id

                session = StripeService.create_checkout_session(
                    email=request.user.email,
                    price_id=price_id,
                    metadata=metadata,
                )

            return Response({"checkout_url": session.url}, status=200)

        except Exception as e:
            logger.exception("[Checkout] Failed to create session")
            return Response({"detail": str(e)}, status=500)


# ============================
#   USER SUBSCRIPTIONS
# ============================

class UserSubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subs = UserSubscription.objects.filter(
            user=request.user
        ).select_related("plan")

        return Response(
            UserSubscriptionSerializer(subs, many=True).data,
            status=200
        )


# ============================
#   CANCEL SUBSCRIPTION
# ============================

class CancelSubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        import stripe

        sub = UserSubscription.objects.filter(
            user=request.user,
            active=True
        ).first()

        if not sub:
            return Response({"detail": "No active subscription found."}, status=404)

        try:
            with transaction.atomic():
                stripe.Subscription.modify(
                    sub.stripe_subscription_id,
                    cancel_at_period_end=True
                )

                sub.active = False
                sub.end_date = timezone.now()
                sub.save()

            return Response({"detail": "Subscription cancelled successfully."}, status=200)

        except Exception as e:
            logger.exception("[Cancel] Subscription cancellation failed")
            return Response({"detail": str(e)}, status=400)


# ============================
#   STRIPE WEBHOOK
# ============================

class StripeWebhookAPIView(APIView):
    """
    Stripe Webhook Handler
    - Handles checkout.session.completed
    - Handles subscription lifecycle events (created, updated, deleted)
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        # 1️⃣ Verify Stripe signature
        try:
            event = StripeService.verify_webhook(payload, sig_header)
        except Exception as e:
            logger.warning(f"[Stripe] Webhook verification failed: {str(e)}")
            return Response({"detail": "Invalid signature"}, status=400)

        data = event["data"]["object"]
        event_type = event["type"]
        logger.info(f"[Webhook] Received event: {event_type}, ID: {data.get('id')}")

        try:
            # -----------------------------
            # CHECKOUT SESSION COMPLETED
            # -----------------------------
            if event_type == "checkout.session.completed":
                self._handle_checkout_session_completed(data)

            # -----------------------------
            # SUBSCRIPTION STATUS UPDATES
            # -----------------------------
            elif event_type.startswith("customer.subscription."):
                self._handle_subscription_event(data, event_type)

            # Log unhandled events
            else:
                logger.info(f"[Webhook] Unhandled event type: {event_type}")

        except Exception as e:
            logger.exception(f"[Webhook] Processing failed for event {event_type}: {str(e)}")
            return Response({"detail": "Processing failed"}, status=500)

        return Response({"received": True}, status=200)

    # -----------------------------
    # Private Handlers
    # -----------------------------
    @staticmethod
    @transaction.atomic
    def _handle_checkout_session_completed(data: dict):
        """
        Handles checkout.session.completed
        Ensures idempotency by using update_or_create
        """
        user_id = int(data["metadata"]["user_id"])
        plan_id = int(data["metadata"]["plan_id"])
        stripe_subscription_id = data.get("subscription")
        stripe_customer_id = data.get("customer")

        # Deactivate any previous active subscription
        UserSubscription.objects.filter(user_id=user_id, active=True).update(
            active=False,
            end_date=timezone.now()
        )

        # Create or update subscription
        sub, created = UserSubscription.objects.update_or_create(
            stripe_subscription_id=stripe_subscription_id,
            defaults={
                "user_id": user_id,
                "plan_id": plan_id,
                "start_date": timezone.now(),
                "active": True,
                "stripe_customer_id": stripe_customer_id,
            },
        )

        action = "Created" if created else "Updated"
        logger.info(f"[Webhook] {action} subscription {sub.id} for user {user_id}")

    @staticmethod
    @transaction.atomic
    def _handle_subscription_event(data: dict, event_type: str):
        """
        Handles subscription events from Stripe
        """
        subscription_id = data["id"]
        status = data.get("status")

        sub = UserSubscription.objects.filter(stripe_subscription_id=subscription_id).first()
        if not sub:
            logger.warning(f"[Webhook] Subscription {subscription_id} not found in DB")
            return

        # Update subscription status
        previous_active = sub.active
        sub.active = status in ("active", "trialing")
        if status in ("canceled", "unpaid"):
            sub.end_date = timezone.now()
        sub.save()

        logger.info(
            f"[Webhook] Subscription {sub.id} updated: "
            f"status={status}, active {previous_active}->{sub.active}"
        )
