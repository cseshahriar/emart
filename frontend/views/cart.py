from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import CartItem
from catalog.models import Product
from cart.utils import get_or_create_cart


def add_to_cart(request, slug):
    ''' add to cart '''
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
    ''' add to cart and redirect to checkout '''
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
    '''Cart details with update functionality'''
    cart = get_or_create_cart(request)

    if request.method == "POST":
        action = request.POST.get("submit")
        cart_item_id = request.POST.get("cart_item_id")

        try:
            if cart_item_id:
                cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)

                if action == "increment":
                    cart_item.quantity += 1
                    cart_item.save()
                    messages.success(request, f"Quantity updated to {cart_item.quantity}")

                elif action == "decrement":
                    if cart_item.quantity > 1:
                        cart_item.quantity -= 1
                        cart_item.save()
                        messages.success(request, f"Quantity updated to {cart_item.quantity}")
                    else:
                        messages.warning(request, "Minimum quantity is 1")

                elif action == "remove":
                    product_name = cart_item.product.name
                    cart_item.delete()
                    messages.success(request, f"{product_name} removed from cart")

                else:
                    messages.error(request, "Invalid action")

            else:
                messages.error(request, "Item not found")

        except CartItem.DoesNotExist:
            messages.error(request, "Cart item not found")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

        # Redirect to refresh page and show messages
        return redirect('cart_detail')

    # Calculate totals for the template
    cart_items = cart.items.all()
    cart_total = sum(item.total_price for item in cart_items)
    item_count = sum(item.quantity for item in cart_items)

    context = {
        "cart": cart,
        "cart_items": cart_items,
        "cart_total": cart_total,
        "item_count": item_count,
    }

    return render(request, "frontend/pages/cart_detail.html", context)


def checkout_start(request):
    ''' checkout processing '''
    cart = get_or_create_cart(request)
    return render(request, "frontend/pages/checkout.html", {"cart": cart})
