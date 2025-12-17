import logging

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from catalog.models import (  # ProductSpecification,; ProductVariant,
    Category,
    Product,
    ProductFeature,
    ProductImage,
)

logger = logging.getLogger(__name__)


class HomePageView(View):
    template_name = "frontend/pages/home.html"

    def get(self, request):
        """Home page get"""
        base_product_queryset = (
            Product.objects.filter(is_active=True)
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

        slider_products = base_product_queryset.filter(is_slider=True)
        most_popular_product = base_product_queryset.filter(
            is_most_popular=True
        ).first()
        categories = Category.objects.filter(is_active=True, is_featured=True)
        featured_products = base_product_queryset.filter(is_featured=True)
        new_products = base_product_queryset.filter(is_new=True)
        bestseller_products = base_product_queryset.filter(is_bestseller=True)
        top_rated_products = base_product_queryset.filter(is_top_rated=True)

        context = {
            "slider_products": slider_products,
            "most_popular_product": most_popular_product,
            "categories": categories,
            "featured_products": featured_products,
            "new_products": new_products,
            "bestseller_products": bestseller_products,
            "top_rated_products": top_rated_products,
        }
        return render(request, self.template_name, context)


class ProductDetailPageView(View):
    template_name = "frontend/pages/product/detail.html"

    def get(self, request, slug):
        """Product Detail page"""
        product = get_object_or_404(Product, slug=slug)
        variants = product.variants.all()
        variant_colors = []
        for variant in variants:
            colors = list(
                variant.variant_attributes.filter(
                    color__isnull=False
                ).values_list("color__code", flat=True)
            )
            for color in colors:
                variant_colors.append(color)

        logger.info(f"{'*' * 10} variant_colors: {variant_colors}\n")
        features = product.features.all()
        specifications = product.specifications.all()
        context = {
            "product": product,
            "variants": variants,
            "variant_colors": variant_colors,
            "features": features,
            "specifications": specifications,
        }
        return render(request, self.template_name, context)
