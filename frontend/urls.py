from django.urls import path

from frontend.views.home_page import HomePageView, ProductDetailPageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home_page"),
    path(
        "product/<str:slug>/detail",
        ProductDetailPageView.as_view(),
        name="product_detail",
    ),
]
