import logging

from django.contrib import messages

from locations.models import District

logger = logging.getLogger(__name__)


def increment_item(request, cart_item):
    cart_item.quantity += 1
    cart_item.save()
    messages.success(request, f"Quantity updated to {cart_item.quantity}")


def decrement_item(request, cart_item):
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        messages.success(request, f"Quantity updated to {cart_item.quantity}")
    else:
        messages.warning(request, "Minimum quantity is 1")


def remove_item(request, cart_item):
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f"{product_name} removed from cart")


def update_location(request, cart):
    district_id = request.POST.get("district")
    if not district_id:
        return

    district = (
        District.objects.filter(pk=int(district_id))
        .select_related("shipping_zone")
        .first()
    )

    if district:
        cart.district = district
        cart.save()
        messages.success(request, "Deliver location changed")
