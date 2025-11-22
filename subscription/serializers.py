from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ["id", "name", "price", "features", "stripe_price_id"]


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            "id",
            "plan",
            "start_date",
            "end_date",
            "active",
            "stripe_subscription_id",
            "stripe_customer_id",
        ]


class CheckoutSessionSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()

    def validate_plan_id(self, value):
        if not SubscriptionPlan.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid plan ID.")
        return value
