from django import template

register = template.Library()


@register.filter
def modifier(value):
    if value > 0:
        return f"+{value}"
    else:
        return value


@register.filter
def sub(value, arg):
    return value - arg
