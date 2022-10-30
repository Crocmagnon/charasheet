from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from character.models import Character


@login_required
def character_view(request: WSGIRequest, pk: int) -> HttpResponse:
    character = get_object_or_404(Character.objects.select_related("player"), pk=pk)
    context = {"character": character}
    return render(request, "character/view.html", context)


@login_required
def character_health_change(request: WSGIRequest, pk: int) -> HttpResponse:
    character = get_object_or_404(Character, pk=pk)
    value = request.GET.get("value")
    if value == "ko":
        character.health_remaining = 0
    elif value == "max":
        character.health_remaining = character.health_max
    else:
        value = int(value)
        character.health_remaining += value
        character.health_remaining = min(
            [character.health_max, character.health_remaining]
        )
        character.health_remaining = max([0, character.health_remaining])
    character.save(update_fields=["health_remaining"])
    return HttpResponse(character.health_remaining)


@login_required
def character_mana_change(request: WSGIRequest, pk: int) -> HttpResponse:
    character = get_object_or_404(Character, pk=pk)
    value = request.GET.get("value")
    if value == "ko":
        character.mana_remaining = 0
    elif value == "max":
        character.mana_remaining = character.mana_max
    else:
        value = int(value)
        character.mana_remaining += value
        character.mana_remaining = min([character.mana_max, character.mana_remaining])
        character.mana_remaining = max([0, character.mana_remaining])
    character.save(update_fields=["mana_remaining"])
    return HttpResponse(character.mana_remaining)
