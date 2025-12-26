from django.urls import path

from frontend.views import (
    add_to_cart,
    buy_now,
    cart_detail,
    cart_shipping_ajax,
    checkout_start,
    customer_dashboard,
    login_view,
    logout_view,
    order_detail,
    order_success,
    signup_view,
)
from frontend.views.category import CategoryProductView
from frontend.views.home_page import HomePageView, ProductDetailPageView

urlpatterns = [
    # home page
    path("", HomePageView.as_view(), name="home"),
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
    path(
        "order/order_detail/<str:order_number>/",
        order_detail,
        name="order_detail",
    ),
    # auth
    path(
        "login/",
        login_view,
        name="user_login",
    ),
    path(
        "register/",
        signup_view,
        name="user_register",
    ),
    path(
        "logout/",
        logout_view,
        name="user_logout",
    ),
    # dashboard
    path("dashboard/", customer_dashboard, name="customer_dashboard"),
    # category product
    path(
        "category/<str:slug>/",
        CategoryProductView.as_view(),
        name="category_products",
    ),
]
