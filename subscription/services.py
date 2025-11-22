import logging
import stripe
from django.conf import settings

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = "2022-11-15"


class StripeService:

    @staticmethod
    def create_checkout_session(email: str, price_id: str, metadata: dict):
        try:
            session = stripe.checkout.Session.create(
                mode="subscription",
                payment_method_types=["card"],
                customer_email=email,
                line_items=[{"price": price_id, "quantity": 1}],
                success_url=f"{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/cancel",
                metadata=metadata,
            )
            logger.info(f"Stripe checkout session created: {session.id}")
            return session
        except Exception as e:
            logger.exception("Stripe checkout creation failed")
            raise e

    @staticmethod
    def verify_webhook(payload: bytes, sig_header: str):
        try:
            return stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except Exception as e:
            logger.warning("Webhook signature verification failed")
            raise e
