"""
Custom template filters for the library app.
"""

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary."""
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Divide the value by the argument."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def percentage(value, total):
    """Calculate percentage."""
    try:
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def add_str(value, arg):
    """Add string to value."""
    return f"{value}{arg}"

@register.filter
def filter_by_status(queryset, status):
    """Filter loans by status."""
    if hasattr(queryset, 'filter'):
        return queryset.filter(status=status)
    return []

@register.filter
def total_fines(queryset):
    """Calculate total unpaid fines."""
    total = 0
    for item in queryset:
        if hasattr(item, 'fine_amount') and hasattr(item, 'fine_paid'):
            if item.fine_amount and not item.fine_paid:
                total += float(item.fine_amount)
    return f"{total:.2f}"