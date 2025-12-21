# ==================== Payment Models ====================
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models

from core.models import BaseModel
from orders.models import Order

User = get_user_model()


class PaymentGateway(BaseModel):
    """Payment gateway configuration"""

    GATEWAY_TYPE_CHOICES = [
        ("bkash", "bKash"),
        ("nagad", "Nagad"),
        ("rocket", "Rocket"),
        ("sslcommerz", "SSLCommerz"),
        ("stripe", "Stripe"),
        ("paypal", "PayPal"),
        ("bank_transfer", "Bank Transfer"),
        ("cod", "Cash on Delivery"),
    ]

    name = models.CharField(max_length=100)
    gateway_type = models.CharField(
        max_length=20, choices=GATEWAY_TYPE_CHOICES, unique=True
    )

    # Credentials (encrypted in production)
    api_key = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    merchant_id = models.CharField(max_length=200, blank=True)

    # Configuration
    # is_active = models.BooleanField(default=False)
    is_test_mode = models.BooleanField(default=True)

    # Display
    logo = models.ImageField(
        upload_to="payment_gateways/", blank=True, null=True
    )
    description = models.TextField(blank=True)
    instructions = models.TextField(
        blank=True, help_text="Instructions shown to customers"
    )

    # Fees
    transaction_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal(0),
        help_text="Percentage fee charged",
    )
    transaction_fee_fixed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal(0),
        help_text="Fixed fee per transaction",
    )

    # Order
    # order = models.PositiveIntegerField(default=0)  # serial
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["serial", "name"]

    def __str__(self):
        return f"{self.name} ({'Test' if self.is_test_mode else 'Live'})"

    def calculate_fee(self, amount):
        """Calculate transaction fee for given amount"""
        percentage_fee = (amount * self.transaction_fee_percentage) / 100
        return percentage_fee + self.transaction_fee_fixed


class Payment(BaseModel):
    """Payment transactions"""

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
        ("partially_refunded", "Partially Refunded"),
    ]

    # Payment Info
    payment_id = models.CharField(max_length=100, unique=True)
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name="payments"
    )
    payment_gateway = models.ForeignKey(
        PaymentGateway, on_delete=models.PROTECT, related_name="payments"
    )

    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0)
    )
    net_amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Amount after fees"
    )
    currency = models.CharField(max_length=3, default="BDT")

    # Status
    status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )

    # Gateway Response
    transaction_id = models.CharField(
        max_length=200, blank=True, help_text="Gateway transaction ID"
    )
    gateway_response = models.JSONField(
        null=True, blank=True, help_text="Full gateway response"
    )

    # Customer Details (snapshot)
    customer_name = models.CharField(max_length=200, blank=True)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)

    # Additional Info
    payment_method_details = models.CharField(
        max_length=200, blank=True, help_text="e.g., bKash: 01712345678"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Notes
    notes = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)

    # Timestamps
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["payment_id"]),
            models.Index(fields=["transaction_id"]),
            models.Index(fields=["order", "-created_at"]),
        ]

    def __str__(self):
        return f"Payment {self.payment_id} - {self.order.order_number} \
            (৳{self.amount})"

    def save(self, *args, **kwargs):
        if not self.payment_id:
            import uuid

            self.payment_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"

        # Calculate net amount
        self.net_amount = self.amount - self.transaction_fee

        super().save(*args, **kwargs)


class Refund(BaseModel):
    """Refund transactions"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    REFUND_TYPE_CHOICES = [
        ("full", "Full Refund"),
        ("partial", "Partial Refund"),
    ]

    # Refund Info
    refund_id = models.CharField(max_length=100, unique=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.PROTECT, related_name="refunds"
    )
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name="refunds"
    )

    refund_type = models.CharField(max_length=10, choices=REFUND_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Status
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )

    # Gateway Response
    transaction_id = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)

    # Reason
    reason = models.TextField()
    admin_notes = models.TextField(blank=True)

    # Processing
    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_refunds",
    )
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_refunds",
    )

    # Timestamps
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Refund {self.refund_id} - ৳{self.amount}"

    def save(self, *args, **kwargs):
        if not self.refund_id:
            import uuid

            self.refund_id = f"REF-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class PaymentMethodAccount(BaseModel):
    """Store customer's saved payment methods (for future use)"""

    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payment_methods"
    )
    payment_gateway = models.ForeignKey(
        PaymentGateway, on_delete=models.CASCADE
    )

    # Account details (masked)
    account_number = models.CharField(
        max_length=100, help_text="Last 4 digits or masked number"
    )
    account_holder_name = models.CharField(max_length=200)

    # Token (encrypted in production)
    payment_token = models.CharField(
        max_length=500, blank=True, help_text="Gateway payment token"
    )

    is_default = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.payment_gateway.name} - {self.account_number}"

    def save(self, *args, **kwargs):
        if self.is_default:
            PaymentMethodAccount.objects.filter(
                customer=self.customer, is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)
