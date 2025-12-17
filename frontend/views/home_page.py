from django.db.models import Prefetch
from django.shortcuts import render
from django.views.generic import View

from catalog.models import (  # ProductSpecification,; ProductVariant,
    Product,
    ProductFeature,
    ProductImage,
)


class HomePageView(View):
    template_name = "frontend/pages/home.html"

    def get(self, request):
        """
        product status:
            is_featured
            is_new
            is_bestseller
            is_top_rated
            is_most_popular
            is_slider
        """
        slider_products = (
            Product.objects.filter(is_active=True, is_slider=True)
            .select_related("category", "brand")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.filter(is_primary=True),
                    to_attr="primary_images",
                ),
                Prefetch(
                    "features",
                    queryset=ProductFeature.objects.all().order_by("order"),
                ),
            )
        )
        most_popular_product = (
            Product.objects.filter(is_active=True, is_most_popular=True)
            .select_related("category")
            .prefetch_related("images")
            .order_by("-sale_count")
            .first()
        )
        print("most_popular_product -----------", most_popular_product)
        context = {
            "slider_products": slider_products,
            "most_popular_product": most_popular_product,
        }
        return render(request, self.template_name, context)
