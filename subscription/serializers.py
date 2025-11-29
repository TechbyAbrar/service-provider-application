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
    
    
# subscriptions/serializers.py
class SubscriptionPlanUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ("name", "features")   # update-only fields



class EarnListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source = 'user.full_name', read_only=True)
    transaction_id = serializers.CharField(source = 'stripe_subscription_id', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_price = serializers.DecimalField(source='plan.price', max_digits=8, decimal_places=2, read_only=True)
    
    class Meta:
        model = UserSubscription
        fields = [
            "id",
            "full_name",
            "transaction_id",
            "plan_name",
            "plan_price",
            "start_date",
            "active",
        ]