# core/templatetags/core_tags.py
from django import template

register = template.Library()


@register.simple_tag
def active_class(request, url_name):
    """
    {% load core_tags %}
    <li class="{% active_class request 'home' %}">Home</li>
    """
    return "active" if request.resolver_match.url_name == url_name else ""
