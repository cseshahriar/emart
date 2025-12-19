# accounts/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from orders.models import Order  # assuming you have an Order model


@login_required
def customer_dashboard(request):
    user = request.user
    # Get recent orders (latest 5)
    recent_orders = Order.objects.filter(customer=user).order_by(
        "-created_at"
    )[:5]

    # Example stats
    total_orders = Order.objects.filter(customer=user).count()
    pending_orders = Order.objects.filter(
        customer=user, order_status="pending"
    ).count()

    context = {
        "user": user,
        "recent_orders": recent_orders,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
    }
    return render(request, "accounts/dashboard.html", context)
