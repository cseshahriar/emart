import logging

from django.contrib import messages
from django.shortcuts import redirect, render

from cart.utils import get_or_create_cart
from locations.models import District
from orders.models import Order
from orders.services import create_order_from_cart
from users.models import Address

logger = logging.getLogger(__name__)


def checkout_start(request):
    """checkout processing"""
    districts = District.objects.filter(is_active=True)
    cart = get_or_create_cart(request)
    district = cart.district
    if not cart or not cart.items.exists():
        return redirect("cart_detail")

    if request.method == "POST":  # checkout post make order
        payment_method = request.POST.get("payment_method") or "cod"
        name = request.POST.get("name")
        address_line1 = request.POST.get("address")
        district = request.POST.get("district")
        phone = request.POST.get("phone")
        postal_code = request.POST.get("postal_code")
        customer_notes = request.POST.get("note")

        # Get user default shipping address
        shipping_address = request.user.addresses.filter(
            is_default_shipping=True
        ).first()

        if not shipping_address:
            shipping_address, _ = Address.objects.get_or_create(
                phone=phone,
                defaults={
                    "session_key": cart.session_key,
                    "full_name": name,
                    "phone": phone,
                    "address_line1": address_line1,
                    "district": cart.district,
                    "postal_code": postal_code,
                    "is_default_shipping": True,
                },
            )

        if name and address_line1 and district and phone and postal_code:
            order = create_order_from_cart(
                cart=cart,
                payment_method=payment_method,
                shipping_address=shipping_address,
                customer_notes=customer_notes,
            )
            messages.warning(
                request,
                "Order has been placed successfully. \
                A person will call you for confirmation!",
            )
            return redirect("order_success", order_number=order.order_number)
        else:
            messages.warning(request, "Invalid form!")

    context = {
        "districts": districts,
        "district": district,
        "cart": cart,
    }
    return render(request, "frontend/pages/checkout.html", context)


def order_success(request, order_number):
    """Order success page"""
    order = Order.objects.filter(order_number=order_number).first()
    context = {"order": order}
    return render(request, "frontend/pages/order_success.html", context)


def order_detail(request, order_number):
    """Order success page"""
    order = Order.objects.filter(order_number=order_number).first()
    context = {"order": order}
    return render(request, "frontend/pages/order_details.html", context)
