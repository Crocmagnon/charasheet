from django import template

from character.models import Character, Path, Weapon
from common.models import User

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


@register.filter
def has_next_capability(path: Path, character: Character) -> bool:
    return path.has_next_capability(character)


@register.filter
def max_rank(path: Path, character: Character) -> int:
    return path.max_rank(character)


@register.filter
def managed_by(character: Character, user: User) -> bool:
    return character.managed_by(user)


@register.filter
def mastered_by(character: Character, user: User) -> bool:
    return character.mastered_by(user)
