# admin.py
from django.contrib import admin
from .models import Supplier, Resource, Task, Notification

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_name', 'supplier_email', 'phone_number', 'created_at']

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'email', 'phone_number', 'start_time', 'end_time']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'status', 'time', 'resource', 'materials_ordered']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['message', 'created_at', 'read']
    list_filter = ['read', 'created_at']
