# core/context_processors.py
from django.conf import settings
from django.contrib.sites.models import Site

from cart.utils import get_or_create_cart
from catalog.models import Category


def common_data(request):
    """return all common data for all templates"""
    categories = Category.objects.filter(
        parent__isnull=True, is_active=True
    ).prefetch_related("children")
    main_menu_categories = Category.objects.filter(
        parent__isnull=True, is_main_menu=True
    ).prefetch_related("children")
    cart = get_or_create_cart(request)
    current_site = Site.objects.get_current()
    return {
        "categories": categories,
        "main_menu_categories": main_menu_categories,
        "cart": cart,
        "SITE_NAME": settings.SITE_NAME,
        "SITE_DOMAIN": current_site.domain,  # ✅ added
        "SITE_OBJECT": current_site,  # optional but useful
    }
