import logging

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import Cart, CartItem
from cart.utils import get_or_create_cart
from catalog.models import Product
from frontend.functions import (
    decrement_item,
    increment_item,
    remove_item,
    update_location,
)
from locations.models import District

logger = logging.getLogger(__name__)


ACTION_HANDLERS = {
    "increment": increment_item,
    "decrement": decrement_item,
    "remove": remove_item,
}


def add_to_cart(request, slug):
    """add to cart"""
    product = get_object_or_404(Product, slug=slug)
    cart = get_or_create_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=None,  # Todo: later you can handle variants
        defaults={"quantity": 1},
    )

    if not created:
        item.quantity += 1
        item.save()

    return redirect("cart_detail")


def buy_now(request, slug):
    """add to cart and redirect to checkout"""
    product = get_object_or_404(Product, slug=slug)
    cart = get_or_create_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=None,
        defaults={"quantity": 1},
    )

    if not created:
        item.quantity += 1
        item.save()

    return redirect("checkout")  # 🔥 DIRECT CHECKOUT


def cart_detail(request):
    """Cart details with update functionality"""
    districts = District.objects.filter(is_active=True).select_related(
        "shipping_zone"
    )
    cart = get_or_create_cart(request)

    if request.method == "POST":
        action = request.POST.get("submit")
        cart_item_id = request.POST.get("cart_item_id")

        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)

            if action in ACTION_HANDLERS:
                ACTION_HANDLERS[action](request, cart_item)
            elif action == "location":
                update_location(request, cart)
            else:
                messages.error(request, "Invalid action")

        except CartItem.DoesNotExist:
            messages.error(request, "Cart item not found")
        except Exception as exc:
            messages.error(request, f"Error: {exc}")

        return redirect("cart_detail")

    cart_items = cart.items.all()
    cart_total = sum(item.total_price for item in cart_items)
    item_count = sum(item.quantity for item in cart_items)

    return render(
        request,
        "frontend/pages/cart_detail.html",
        {
            "cart": cart,
            "districts": districts,
            "cart_items": cart_items,
            "cart_total": cart_total,
            "item_count": item_count,
        },
    )


def cart_shipping_ajax(request):
    logger.info(f"{'*' * 10} cart_shipping_ajax called\n")
    district_id = request.GET.get("district_id")
    cart_id = request.GET.get("cart_id")

    # name = request.GET.get("name")
    # address = request.GET.get("address")
    # phone = request.GET.get("phone")
    # post_code = request.GET.get("post_code")
    # note = request.GET.get("note")

    if district_id and cart_id:
        cart = Cart.objects.filter(pk=int(cart_id)).first()
        district = District.objects.filter(pk=district_id).first()
        if cart and district:
            cart.district = district
            cart.save()
            return JsonResponse(
                {
                    "success": True,
                    "shipping_charge": cart.get_shipping_charge,
                    "grand_total": cart.grand_total,
                    "message": "আপনার ঠিকানা অনুযায়ী শিপিং চার্জ আপডেট হয়েছে।",
                },
                status=200,
            )
    return JsonResponse(
        {"success": False, "message": "Cart not found"}, status=404
    )
