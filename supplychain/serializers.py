from rest_framework import serializers
from .models import Supplier, Resource, Task, Notification


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'supplier_name', 'supplier_email', 'phone_number', 'profile_picture', 'materials_supplied', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
        

class ResourceSerializer(serializers.ModelSerializer):
    # Make 'days' a list in the API
    days = serializers.ListField(
        child=serializers.ChoiceField(choices=[day[0] for day in Resource.DAYS_OF_WEEK])
    )

    class Meta:
        model = Resource
        fields = [
            'id', 'name', 'role', 'email', 'phone_number',
            'add_to_calender', 'days', 'start_time', 'end_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


import json
from rest_framework import serializers

import json
from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    user_id = serializers.CharField()
    bill_of_materials = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id", "user_id", "customer_name", "phone_number", "address",
            "task_description", "bill_of_materials", "time", "resource",
            "status", "materials_ordered", "price",  "timestamp", "created_at", "updated_at"
        ]

    def get_bill_of_materials(self, obj):
        try:
            return json.loads(obj.bill_of_materials)
        except:
            return []

    def get_price(self, obj):
        try:
            return json.loads(obj.price)
        except:
            return {}




# Notification
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at', 'read']