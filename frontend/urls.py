from django.urls import path

from frontend.views import (
    add_to_cart,
    buy_now,
    cart_detail,
    cart_shipping_ajax,
    checkout_start,
    order_success,
)
from frontend.views.home_page import HomePageView, ProductDetailPageView

urlpatterns = [
    # home page
    path("", HomePageView.as_view(), name="home_page"),
    # product
    path(
        "product/<str:slug>/detail",
        ProductDetailPageView.as_view(),
        name="product_detail",
    ),
    # cart
    path("add-to-cart/<slug:slug>/", add_to_cart, name="add_to_cart"),
    path("buy-now/<slug:slug>/", buy_now, name="buy_now"),
    path("cart/", cart_detail, name="cart_detail"),
    path("cart_shipping_ajax/", cart_shipping_ajax, name="cart_shipping_ajax"),
    # checkout
    path("checkout/", checkout_start, name="checkout"),
    path(
        "order/success/<str:order_number>/",
        order_success,
        name="order_success",
    ),
]
