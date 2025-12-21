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


# def cart_detail(request):
#     """Cart details with update functionality"""
#     print(f"{'*' * 10} cart_detail called \n")
#     districts = District.objects.filter(is_active=True).select_related(
#         "shipping_zone"
#     )
#     cart = get_or_create_cart(request)

#     if request.method == "POST":
#         print(f"{'*' * 10} post block \n")
#         action = request.POST.get("submit")
#         cart_item_id = request.POST.get("cart_item_id")
#         print("action ", action)
#         print("cart_item_id ", cart_item_id)
#         try:
#             cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
#             if action == "increment":
#                 cart_item.quantity += 1
#                 cart_item.save()
#                 messages.success(
#                     request, f"Quantity updated to {cart_item.quantity}"
#                 )
#             elif action == "decrement":
#                 if cart_item.quantity > 1:
#                     cart_item.quantity -= 1
#                     cart_item.save()
#                     messages.success(
#                         request,
#                         f"Quantity updated to {cart_item.quantity}",
#                     )
#                 else:
#                     messages.warning(request, "Minimum quantity is 1")
#             elif action == "remove":
#                 product_name = cart_item.product.name
#                 cart_item.delete()
#                 messages.success(request, f"{product_name} removed from cart")
#             elif action == "location":
#                 district_id = request.POST.get("district")
#                 print(f"{'*' * 10} district_id: {district_id}\n")
#                 if district_id:
#                     district = District.objects.filter(
#                         pk=int(district_id)
#                     ).select_related("shipping_zone")
#                     if district and cart:
#                         cart.district = district
#                         cart.save()
#                         messages.success(request, "Deliver location changed")
#             else:
#                 messages.error(request, "Item not found")

#         except CartItem.DoesNotExist:
#             messages.error(request, "Cart item not found")
#         except Exception as e:
#             messages.error(request, f"Error: {str(e)}")

#         # Redirect to refresh page and show messages
#         return redirect("cart_detail")

#     # get method
#     # Calculate totals for the template
#     cart_items = cart.items.all()
#     cart_total = sum(item.total_price for item in cart_items)
#     item_count = sum(item.quantity for item in cart_items)

#     context = {
#         "cart": cart,
#         "districts": districts,
#         "cart_items": cart_items,
#         "cart_total": cart_total,
#         "item_count": item_count,
#     }

#     return render(request, "frontend/pages/cart_detail.html", context)


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

    if district_id and cart_id:
        cart = Cart.objects.filter(pk=int(cart_id)).first()
        district = District.objects.filter(pk=district_id).first()
        if cart and district:
            cart.district = district
            cart.save()
            logger.info(f"{'*' * 10} cart district updated \n")
            data = {"message": "Success"}
            return JsonResponse(data, status=200)

    return JsonResponse(
        {"success": False, "message": "Cart not found"}, status=404
    )
