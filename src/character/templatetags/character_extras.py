from django import template

from character.models import Character, Weapon

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


@register.filter
def weapon_modifier(character: Character, weapon: Weapon):
    value = character.get_modifier_for_weapon(weapon)
    if value > 0:
        return f"+ {value}"
    elif value < 0:
        return f"- {abs(value)}"
    else:
        return ""
