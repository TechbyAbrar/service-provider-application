# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Supplier, Resource, Task, Notification

@receiver(post_save, sender=Supplier)
def notify_admin_supplier(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(message=f"New Supplier created: {instance.supplier_name}")

@receiver(post_save, sender=Resource)
def notify_admin_resource(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(message=f"New Resource created: {instance.name}")

@receiver(post_save, sender=Task)
def notify_admin_task(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(message=f"New Task created for customer: {instance.customer_name}")
