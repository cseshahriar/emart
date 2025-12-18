# core/context_processors.py
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
    return {
        "categories": categories,
        "main_menu_categories": main_menu_categories,
        "cart": cart,
    }
