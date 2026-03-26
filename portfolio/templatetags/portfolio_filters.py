from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Split a string by the given argument"""
    if value:
        return value.split(arg)
    return []

@register.filter
def strip(value):
    """Strip whitespace from a string"""
    if value:
        return value.strip()
    return value

@register.filter
def get_tech_list(technologies):
    """Convert comma-separated technologies to list"""
    if technologies:
        return [tech.strip() for tech in technologies.split(',')]
    return []

@register.filter
def get_first_tech(technologies):
    """Get first technology from comma-separated list"""
    if technologies:
        return technologies.split(',')[0].strip()
    return ''