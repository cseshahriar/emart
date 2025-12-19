import logging

from django.contrib import messages
from django.shortcuts import redirect, render

from cart.utils import get_or_create_cart
from locations.models import District
from orders.services import create_order_from_cart
from orders.utils import get_order

logger = logging.getLogger(__name__)


def checkout_start(request):
    """checkout processing"""
    districts = District.objects.filter(is_active=True)
    cart = get_or_create_cart(request)
    district = cart.district
    logger.info(f"{'*' * 10} cart: {cart}\n")

    if not cart or not cart.items.exists():
        return redirect("cart_detail")

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        shipping_address = request.user.addresses.filter(is_default=True).first()

        order = create_order_from_cart(
            cart=cart,
            payment_method=payment_method,
            shipping_address=shipping_address,
        )

        return redirect("order_success", order_number=order.order_number)

    context = {
        "districts": districts,
        "district": district,
        "cart": cart,
    }
    return render(
        request,
        "frontend/pages/checkout.html",
        context
    )


def order_success(request):
    ''' Order success page '''
    order = get_order(request)
    context = {"order": order}
    return render(
        request,
        "frontend/pages/order_success.html",
        context
    )
