from users.models import Address


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
