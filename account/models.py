from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.core.validators import RegexValidator
from .managers import UserManager
from .utils import generate_otp, get_otp_expiry, validate_image


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]
        

    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(r"^\+?\d{9,15}$", message="Phone number must be valid")]
    )
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=100)

    profile_pic = models.ImageField(
        upload_to="profile/",
        default="profile/profile.png",
        null=True,
        blank=True,
        validators=[validate_image],
    )
    profile_pic_url = models.URLField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expired = models.DateTimeField(blank=True, null=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    bio = models.TextField(max_length=255, blank=True, null=True)
    
    company_name = models.CharField(max_length=255, null=True, blank=True)
    cvr_number = models.IntegerField(unique=True, null=True, blank=True)
    
    bank_name = models.CharField(max_length=155, null=True, blank=True)
    account_number = models.IntegerField(null=True, blank=True)
    
    iban = models.CharField(max_length=255, null=True, blank=True)
    swift_ibc = models.CharField(max_length=255, blank=True, null=True)
    
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profit_on_materials = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    risk_margin = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    last_activity = models.DateTimeField(null=True, blank=True)


    # Required by Django
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"] # Fields required when creating superuser 
    # "username", "phone"
    objects = UserManager()

    def __str__(self):
        return self.username or self.email or self.phone or f"User-{self.pk}"

    def get_full_name(self):
        return self.full_name

    def set_otp(self, otp: str = None, expiry_minutes: int = 30) -> None:
        self.otp = otp or generate_otp()
        self.otp_expired = get_otp_expiry(expiry_minutes)

    def is_otp_valid(self, otp: str) -> bool:
        return self.otp == otp and self.otp_expired and timezone.now() <= self.otp_expired
