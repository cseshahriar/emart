# cart/utils.py
from orders.models import Order


def get_order(request):
    ''' return latest order but user or session'''
    if request.user.is_authenticated:
        order = Order.objects.filter(customer=request.user).latest()
    else:
        if not request.session.session_key:
            request.session.create()
        order = Order.objects.filter(
            session_key=request.session.session_key
        ).latest()
    return order
