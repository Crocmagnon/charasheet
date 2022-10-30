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
    value = get_updated_value(request, character.health_remaining, character.health_max)
    character.health_remaining = value
    character.save(update_fields=["health_remaining"])
    return HttpResponse(value)


@login_required
def character_mana_change(request: WSGIRequest, pk: int) -> HttpResponse:
    character = get_object_or_404(
        Character.objects.only(
            "mana_remaining", "level", "value_intelligence", "profile"
        ).select_related("profile"),
        pk=pk,
    )
    value = get_updated_value(request, character.mana_remaining, character.mana_max)
    character.mana_remaining = value
    character.save(update_fields=["mana_remaining"])
    return HttpResponse(value)


@login_required
def character_recovery_points_change(request: WSGIRequest, pk: int) -> HttpResponse:
    character = get_object_or_404(
        Character.objects.only("recovery_points_remaining"), pk=pk
    )
    value = get_updated_value(
        request, character.recovery_points_remaining, character.recovery_points_max
    )
    character.recovery_points_remaining = value
    character.save(update_fields=["recovery_points_remaining"])
    return HttpResponse(value)


@login_required
def character_luck_points_change(request: WSGIRequest, pk: int) -> HttpResponse:
    character = get_object_or_404(
        Character.objects.only("luck_points_remaining", "value_charisma"), pk=pk
    )
    value = get_updated_value(
        request, character.luck_points_remaining, character.luck_points_max
    )
    character.luck_points_remaining = value
    character.save(update_fields=["luck_points_remaining"])
    return HttpResponse(value)


def get_updated_value(
    request: WSGIRequest, remaining_value: int, max_value: int
) -> int:
    form_value = request.GET.get("value")
    if form_value == "ko":
        remaining_value = 0
    elif form_value == "max":
        remaining_value = max_value
    else:
        form_value = int(form_value)
        remaining_value += form_value
        remaining_value = min([max_value, remaining_value])
        remaining_value = max([0, remaining_value])
    return remaining_value


@login_required
def character_notes_change(request: WSGIRequest, pk: int) -> HttpResponse:
    return update_text_field(request, pk, "notes")


@login_required
def character_equipment_change(request: WSGIRequest, pk: int) -> HttpResponse:
    return update_text_field(request, pk, "equipment")


def update_text_field(request, pk, field):
    character = get_object_or_404(Character.objects.only(field), pk=pk)
    context = {"character": character}
    if request.method == "GET":
        return render(request, f"character/{field}_update.html", context)
    setattr(character, field, request.POST.get(field))
    character.save(update_fields=[field])
    return render(request, f"character/{field}_display.html", context)
