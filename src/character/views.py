from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from character.models import Character


@login_required
def character_view(request: WSGIRequest, pk: int) -> HttpResponse:
    character = get_object_or_404(
        Character.objects.select_related(
            "player", "racial_capability", "profile", "race"
        ).prefetch_related("capabilities__path", "weapons"),
        pk=pk,
    )
    context = {"character": character}
    return render(request, "character/view.html", context)


@login_required
def character_health_change(request: WSGIRequest, pk: int) -> HttpResponse:
    character = get_object_or_404(
        Character.objects.only("health_max", "health_remaining"), pk=pk
    )
    value = get_updated_value(character.health_max, request)
    character.health_remaining = value
    character.save(update_fields=["health_remaining"])
    return HttpResponse(character.health_remaining)


@login_required
def character_mana_change(request: WSGIRequest, pk: int) -> HttpResponse:
    character = get_object_or_404(
        Character.objects.only("mana_remaining", "level", "value_intelligence"), pk=pk
    )
    value = get_updated_value(character.mana_max, request)
    character.mana_remaining = value
    character.save(update_fields=["mana_remaining"])
    return HttpResponse(character.mana_remaining)


@login_required
def character_notes_change(request: WSGIRequest, pk: int) -> HttpResponse:
    character = get_object_or_404(Character.objects.only("notes"), pk=pk)
    context = {"character": character}
    if request.method == "GET":
        return render(request, "character/notes_update.html", context)

    character.notes = request.POST.get("notes")
    character.save()
    return render(request, "character/notes_display.html", context)


def get_updated_value(max_value, request):
    value = request.GET.get("value")
    if value == "ko":
        value = 0
    elif value == "max":
        value = max_value
    else:
        value = int(value)
        value += value
        value = min([max_value, value])
        value = max([0, value])
    return value
