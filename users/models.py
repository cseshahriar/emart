import re

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(
        self, email=None, phone=None, password=None, **extra_fields
    ):
        """Create and save a User with either email or phone"""
        if not email and not phone:
            raise ValueError("Either Email or Phone must be set")

        user = self.model(
            email=self.normalize_email(email) if email else None,
            phone=self.normalize_phone(phone) if phone else None,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email=None, phone=None, password=None, **extra_fields
    ):
        """Create and save a SuperUser"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not email and not phone:
            raise ValueError("Superuser must have either email or phone")

        return self.create_user(email, phone, password, **extra_fields)

    def normalize_phone(self, phone):
        """Normalize phone numbers by removing non-digit characters"""
        if phone:
            return re.sub(r"\D", "", phone)
        return phone


class User(AbstractBaseUser, PermissionsMixin):
    # Authentication fields
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)

    # User info
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    username = models.CharField(
        max_length=30, unique=True, null=True, blank=True
    )

    # Status fields
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    phone_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, null=True, blank=True
    )

    # Social login fields
    facebook_id = models.CharField(max_length=100, blank=True, null=True)
    google_id = models.CharField(max_length=100, blank=True, null=True)
    github_id = models.CharField(max_length=100, blank=True, null=True)

    # Profile
    profile_picture = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True
    )
    bio = models.TextField(blank=True)
    otp = models.CharField(max_length=8, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"  # Default login field
    REQUIRED_FIELDS = []  # No required fields for createsuperuser

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email or self.phone or str(self.id)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    @property
    def login_identifier(self):
        """Return the identifier used for login (email or phone)"""
        return self.email or self.phone


class Address(models.Model):
    """Customer addresses"""

    ADDRESS_TYPE_CHOICES = [
        ("billing", "Billing"),
        ("shipping", "Shipping"),
    ]
    session_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
    )
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="addresses", null=True
    )
    address_type = models.CharField(
        max_length=10, choices=ADDRESS_TYPE_CHOICES
    )

    # Contact
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    # Address
    address_line1 = models.CharField(max_length=500)
    address_line2 = models.CharField(max_length=500, blank=True)
    district = models.ForeignKey(
        "locations.District",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="addresses",
    )
    # upazila = models.ForeignKey(Upazila, on_delete=models.PROTECT)
    postal_code = models.CharField(max_length=10, blank=True)

    # Defaults
    is_default_billing = models.BooleanField(default=False)
    is_default_shipping = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.full_name} - {self.address_line1}"

    def save(self, *args, **kwargs):
        # ================================
        # AUTO CREATE / ASSIGN USER BY PHONE
        # ================================
        if self.phone and not self.customer:
            user, created = User.objects.get_or_create(
                phone=self.phone,
                defaults={
                    "username": self.phone,
                    "email": self.email or "",
                },
            )
            self.customer = user

        # Ensure only one default per type per customer
        if self.is_default_billing:
            Address.objects.filter(
                customer=self.customer,
                address_type=self.address_type,
                is_default_billing=True,
            ).update(is_default_billing=False)

        if self.is_default_shipping:
            Address.objects.filter(
                customer=self.customer,
                address_type=self.address_type,
                is_default_shipping=True,
            ).update(is_default_shipping=False)

        super().save(*args, **kwargs)
