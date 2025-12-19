import random
from decimal import Decimal

from django.utils import timezone

from shipping.models import ShippingSetting
from users.models import Address, User


def get_default_shipping_address(user):
    address, _ = Address.objects.get_or_create(
        customer=user, address_type="shipping", is_default_shipping=True
    )
    return address


def get_guest_shipping_address(request):
    address, _ = Address.objects.get_or_create(
        session_key=request.session.session_key,
        address_type="shipping",
        is_default_shipping=True,
    )
    return address


def calculate_shipping(
    *,
    shipping_method,
    weight_kg,
    order_amount,
    is_cod=False,
):
    """
    Returns total shipping charge
    """

    # Base price (up to 1kg)
    total = Decimal(shipping_method.base_price)

    # Extra weight charge
    if weight_kg > shipping_method.max_weight_kg:
        extra_kg = weight_kg - shipping_method.max_weight_kg
        total += extra_kg * shipping_method.extra_price_per_kg

    # COD charge (1%)
    if is_cod:
        settings = ShippingSetting.objects.first()
        cod_charge = (settings.cod_percentage / 100) * order_amount
        total += cod_charge

    # VAT
    settings = ShippingSetting.objects.first()
    vat = (settings.vat_percentage / 100) * total
    total += vat

    return total.quantize(Decimal("0.01"))


def opt_generation(phone: str):
    """OTP generation and store user model"""
    if len(phone) == 1:
        user, created = User.objects.get_or_create(phone=phone)
        otp = str(random.randint(100000, 999999))
        if user:
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            return otp
    return None
