# cart/utils.py
from cart.models import Cart
from locations.models import District


def get_or_create_cart(request):
    district = District.objects.filter(name="Dhaka").first()
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(customer=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(
            session_key=request.session.session_key
        )

    if (
        cart and not cart.district and district
    ):  # cart default set inside dhaka
        cart.district = district
        cart.save()

    return cart
