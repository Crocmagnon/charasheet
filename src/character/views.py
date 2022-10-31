from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django_htmx.http import trigger_client_event

from character.forms import EquipmentForm
from character.models import Character


@login_required
def characters_list(request):
    context = {
        "characters": Character.objects.filter(player=request.user).select_related(
            "race", "profile"
        )
    }
    return render(request, "character/list.html", context)


@login_required
def character_view(request, pk: int):
    character = get_object_or_404(
        Character.objects.select_related(
            "player", "racial_capability", "profile", "race"
        ).prefetch_related("capabilities__path", "weapons"),
        pk=pk,
    )
    context = {"character": character}
    return render(request, "character/view.html", context)


@login_required
def character_health_change(request, pk: int):
    character = get_object_or_404(
        Character.objects.only("health_max", "health_remaining"), pk=pk
    )
    value = get_updated_value(request, character.health_remaining, character.health_max)
    character.health_remaining = value
    character.save(update_fields=["health_remaining"])
    return HttpResponse(value)


@login_required
def character_mana_change(request, pk: int):
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
def character_recovery_points_change(request, pk: int):
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
def character_defense_misc_change(request, pk: int):
    character = get_object_or_404(Character.objects.only("defense_misc"), pk=pk)
    value = get_updated_value(request, character.defense_misc, float("inf"))
    character.defense_misc = value
    character.save(update_fields=["defense_misc"])
    response = HttpResponse(value)
    return trigger_client_event(response, "update_defense", {})


@login_required
def character_luck_points_change(request, pk: int):
    character = get_object_or_404(
        Character.objects.only("luck_points_remaining", "value_charisma"), pk=pk
    )
    value = get_updated_value(
        request, character.luck_points_remaining, character.luck_points_max
    )
    character.luck_points_remaining = value
    character.save(update_fields=["luck_points_remaining"])
    return HttpResponse(value)


def get_updated_value(request, remaining_value: int, max_value: int | float) -> int:
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
def character_get_defense(request, pk: int):
    character = get_object_or_404(
        Character.objects.only("defense_misc", "armor", "shield", "value_dexterity"),
        pk=pk,
    )
    return HttpResponse(character.defense)


@login_required
def character_notes_change(request, pk: int):
    return update_text_field(request, pk, "notes")


@login_required
def character_equipment_change(request, pk: int):
    field = "equipment"
    character = get_object_or_404(Character.objects.only(field), pk=pk)
    context = {"character": character}
    if request.method == "GET":
        return render(request, f"character/{field}_update.html", context)
    form = EquipmentForm(request.POST, instance=character)
    if form.is_valid():
        form.save()
        return render(request, f"character/{field}_display.html", context)
    else:
        context["errors"] = form.errors
        return render(request, f"character/{field}_update.html", context)


@login_required
def character_damage_reduction_change(request, pk: int):
    return update_text_field(request, pk, "damage_reduction")


def update_text_field(request, pk, field):
    character = get_object_or_404(Character.objects.only(field), pk=pk)
    context = {"character": character}
    if request.method == "GET":
        return render(request, f"character/{field}_update.html", context)
    setattr(character, field, request.POST.get(field))
    character.save(update_fields=[field])
    return render(request, f"character/{field}_display.html", context)
