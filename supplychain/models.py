from django.db import models

# Create your models here.
class Supplier(models.Model):
    supplier_name = models.CharField(max_length=255)
    supplier_email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    profile_picture = models.ImageField(upload_to='supplier_profiles/', blank=True, null=True)
    materials_supplied = models.TextField(blank=True, null=True)
    
    role = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    add_to_calender = models.BooleanField(default=False)
    

    def __str__(self):
        return self.supplier_name