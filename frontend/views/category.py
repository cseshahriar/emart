import logging

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from catalog.models import (
    Category,
    Product,
    ProductFeature,
    ProductImage,
)

logger = logging.getLogger(__name__)


class CategoryProductView(View):
    template_name = "frontend/pages/category_product.html"

    def get(self, request, slug):
        """Home page get"""
        category = get_object_or_404(Category, slug=slug)
        object_list = (
            Product.objects.filter(is_active=True, category__slug=slug)
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
        context = {"object_list": object_list, "category": category}
        return render(request, self.template_name, context)
