import logging
import stripe
from django.conf import settings
from django.db import transaction
from .models import SubscriptionPlan

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = "2022-11-15"


class StripeService:

    @staticmethod
    def create_stripe_product(plan: SubscriptionPlan) -> str:

        if plan.stripe_price_id:
            return plan.stripe_price_id

        try:
            with transaction.atomic():
                product = stripe.Product.create(name=plan.name)

                price = stripe.Price.create(
                    unit_amount=int(plan.price * 100),
                    currency="usd",
                    recurring={"interval": "month"},
                    product=product.id,
                )

                plan.stripe_price_id = price.id
                plan.save(update_fields=["stripe_price_id"])

                logger.info(f"[Stripe] Product + price created for plan {plan.id}")

                return price.id

        except Exception as e:
            logger.exception(f"[Stripe] Failed to create Stripe product for plan {plan.id}")
            raise

    @staticmethod
    def create_checkout_session(email: str, price_id: str, metadata: dict):
        try:
            session = stripe.checkout.Session.create(
                mode="subscription",
                payment_method_types=["card"],
                customer_email=email,
                line_items=[{"price": price_id, "quantity": 1}],
                success_url=f"{settings.SUCCESS_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.CANCEL_URL}/cancel",
                metadata=metadata,
            )
            logger.info(f"[Stripe] Checkout session created: {session.id}")
            return session

        except Exception:
            logger.exception("[Stripe] Checkout session creation failed")
            raise

    @staticmethod
    def verify_webhook(payload: bytes, sig_header: str):
        try:
            return stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except Exception:
            logger.warning("[Stripe] Webhook verification failed")
            raise

    @staticmethod
    def deactivate_stripe_product(plan: SubscriptionPlan):
        try:
            price = stripe.Price.retrieve(plan.stripe_price_id)
            product_id = price.product

            # Deactivate the price (hides from dashboard)
            stripe.Price.modify(
                plan.stripe_price_id,
                active=False
            )

            # Deactivate the product
            stripe.Product.modify(
                product_id,
                active=False
            )

            logger.info(f"[Stripe] Deactivated product and price for plan {plan.id}")

        except Exception as e:
            logger.error(f"[Stripe] Failed to deactivate product for plan {plan.id}: {str(e)}")
            # Do NOT raise. We still delete the local plan.