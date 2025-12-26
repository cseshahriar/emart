from decimal import Decimal

from django.db import transaction

from .models import Order, OrderItem


def create_order_from_cart(
    *,
    cart,
    payment_method="cod",
    shipping_address=None,
    billing_address=None,
    shipping_method=None,
    customer_notes=None,
):
    """
    Convert Cart → Order safely
    """

    with transaction.atomic():

        shipping_cost = cart.get_shipping_charge
        cod_charge = cart.get_cod_charge(payment_method)
        # cod charge for merchant

        subtotal = cart.subtotal
        total_amount = (subtotal + shipping_cost).quantize(Decimal("0.01"))
        order = Order.objects.create(
            customer=cart.customer,
            session_key=cart.session_key,
            payment_method=payment_method,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax_amount=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            total_amount=total_amount,
            shipping_method=shipping_method,
            shipping_address=shipping_address,
            billing_address=billing_address,
            customer_notes=customer_notes,
            cod_charge=cod_charge,
        )

        # Copy cart items → order items
        for item in cart.items.select_related("product", "variant"):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                product_name=item.product.name,
                variant_details=str(item.variant) if item.variant else "",
                sku=item.variant.sku if item.variant else item.product.sku,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )

        # Clear cart
        cart.items.all().delete()

        return order
