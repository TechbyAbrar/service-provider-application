from django.db import models
from multiselectfield import MultiSelectField

# Create your models here.
class Supplier(models.Model):
    supplier_name = models.CharField(max_length=255)
    supplier_email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    profile_picture = models.ImageField(upload_to='supplier_profiles/', blank=True, null=True)
    
    materials_supplied = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    

    def __str__(self):
        return self.supplier_name
    
    
class Resource(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    add_to_calender = models.BooleanField(default=False)
    
    days = MultiSelectField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)     
    
    def __str__(self):
        days_str = ', '.join(self.days) if self.days else 'No days'
        return f"{days_str}: {self.start_time} - {self.end_time}"
    
    
# Task Management
import uuid
class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=50)
    address = models.TextField()
    task_description = models.TextField()
    bill_of_materials = models.TextField()  # stored as JSON string
    time = models.DateTimeField()
    resource = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    price = models.TextField()  # MUST be TextField if DB stores JSON
    user_id = models.BigIntegerField()
    materials_ordered = models.BooleanField()
    
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


    class Meta:
        db_table = 'offers'
        managed = False
