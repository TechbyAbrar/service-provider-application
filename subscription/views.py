import logging
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
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
            return Response({"detail": "Admin access only."}, status=403)
        serializer = SubscriptionPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = serializer.save()
        return Response(SubscriptionPlanSerializer(plan).data, status=201)


class CheckoutSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = get_object_or_404(
            SubscriptionPlan.objects.only("id", "stripe_price_id"),
            id=serializer.validated_data["plan_id"],
        )

        session = StripeService.create_checkout_session(
            email=request.user.email,
            price_id=plan.stripe_price_id,
            metadata={"user_id": request.user.id, "plan_id": plan.id},
        )
        return Response({"checkout_url": session.url}, status=200)


class UserSubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subs = UserSubscription.objects.filter(user=request.user).select_related("plan")
        return Response(UserSubscriptionSerializer(subs, many=True).data, status=200)


class StripeWebhookAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            event = StripeService.verify_webhook(payload, sig_header)
        except Exception:
            return Response(status=400)

        data = event["data"]["object"]
        event_type = event["type"]
        logger.info(f"Received event: {event_type}")

        try:
            if event_type == "checkout.session.completed":
                user_id = data["metadata"]["user_id"]
                plan_id = data["metadata"]["plan_id"]
                subscription_id = data.get("subscription")
                customer_id = data.get("customer")

                with transaction.atomic():
                    UserSubscription.objects.filter(user_id=user_id, active=True).update(
                        active=False, end_date=timezone.now()
                    )
                    UserSubscription.objects.create(
                        user_id=user_id,
                        plan_id=plan_id,
                        start_date=timezone.now(),
                        active=True,
                        stripe_subscription_id=subscription_id,
                        stripe_customer_id=customer_id,
                    )
                    logger.info(f"New subscription created for user {user_id}")

            elif event_type.startswith("customer.subscription."):
                subscription_id = data["id"]
                status_stripe = data["status"]
                sub = UserSubscription.objects.filter(
                    stripe_subscription_id=subscription_id
                ).first()
                if sub:
                    with transaction.atomic():
                        sub.active = status_stripe in ("active", "trialing")
                        if status_stripe in ("canceled", "unpaid"):
                            sub.end_date = timezone.now()
                        sub.save()
                        logger.info(f"Updated subscription {sub.id} -> {status_stripe}")
        except Exception as e:
            logger.exception("Error handling webhook: %s", e)
            return Response(status=500)

        return Response(status=200)
