from frontend.views.home_page import HomePageView, ProductDetailPageView

from .auth import login_view, logout_view, signup_view
from .cart import add_to_cart, buy_now, cart_detail, cart_shipping_ajax
from .category import CategoryProductView
from .checkout import checkout_start, order_detail, order_success
from .dashboard import customer_dashboard

__all__ = [
    "HomePageView",
    "ProductDetailPageView",
    "add_to_cart",
    "buy_now",
    "cart_detail",
    "cart_shipping_ajax",
    "checkout_start",
    "order_success",
    "order_detail",
    "login_view",
    "signup_view",
    "logout_view",
    "customer_dashboard",
    "CategoryProductView",
]
