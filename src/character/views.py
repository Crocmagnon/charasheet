from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django_htmx.http import trigger_client_event

from character.forms import AddPathForm, CharacterCreateForm, EquipmentForm
from character.models import Capability, Character, HarmfulState, Path
from character.templatetags.character_extras import modifier
from party.models import Party


@login_required
def characters_list(request):
    context = {
        "characters": Character.objects.owned_by(request.user).select_related(
            "race", "profile"
        ),
        "all_states": HarmfulState.objects.all(),
    }
    return render(request, "character/characters_list.html", context)


@login_required
def character_create(request):
    if request.method == "POST":
        form = CharacterCreateForm(request.POST, request.FILES)
        if form.is_valid():
            character = form.save(commit=False)
            character.player = request.user
            character.recovery_points_remaining = character.recovery_points_max
            character.luck_points_remaining = character.luck_points_max
            character.mana_remaining = character.mana_max
            character.health_remaining = character.health_max
            character.save()
            form.save_m2m()
            messages.success(request, f"{character.name} a été créé.")
            return redirect("character:list")
    else:
        form = CharacterCreateForm()
    context = {"form": form}
    return render(request, "character/character_form.html", context)


@login_required
def character_change(request, pk: int):
    character = get_object_or_404(Character.objects.managed_by(request.user), pk=pk)
    if request.method == "POST":
        form = CharacterCreateForm(request.POST, request.FILES, instance=character)
        if form.is_valid():
            character = form.save()
            messages.success(request, f"{character.name} a été enregistré.")
            return redirect(character.get_absolute_url())
    else:
        form = CharacterCreateForm(instance=character)
    context = {"form": form}
    return render(request, "character/character_form.html", context)


@login_required
def character_delete(request, pk: int):
    character = get_object_or_404(Character.objects.owned_by(request.user), pk=pk)
    context = {"character": character}
    if request.method == "POST":
        name = character.name
        character.delete()
        messages.success(request, f"Le personnage {name} a été supprimé.")
        return redirect("character:list")
    return render(request, "character/character_delete.html", context)


@login_required
def character_view(request, pk: int):
    character = get_object_or_404(
        Character.objects.friendly_to(request.user)
        .select_related("player", "racial_capability", "profile", "race")
        .prefetch_related("capabilities__path", "weapons"),
        pk=pk,
    )
    add_path_form = AddPathForm(character)
    context = {
        "character": character,
        "add_path_form": add_path_form,
        "all_states": HarmfulState.objects.all(),
    }
    party_pk = request.GET.get("party")
    if party_pk:
        context["party"] = get_object_or_404(
            Party.objects.related_to(request.user).prefetch_related("characters"),
            pk=party_pk,
        )
    return render(request, "character/character_details.html", context)


@login_required
def add_path(request, pk: int):
    character = get_object_or_404(Character.objects.managed_by(request.user), pk=pk)
    form = AddPathForm(character, request.POST)
    context = {"character": character}
    if form.is_valid():
        path: Path = form.cleaned_data.get("character_path") or form.cleaned_data.get(
            "other_path"
        )
        cap = path.get_next_capability(character)
        character.capabilities.add(cap)
        context["add_path_form"] = AddPathForm(character)
    else:
        context["add_path_form"] = form
    return render(
        request,
        "character/snippets/character_details/paths_and_capabilities.html",
        context,
    )


@login_required
def character_health_change(request, pk: int):
    character = get_object_or_404(
        Character.objects.managed_by(request.user).only(
            "health_max", "health_remaining"
        ),
        pk=pk,
    )
    value = get_updated_value(request, character.health_remaining, character.health_max)
    character.health_remaining = value
    character.save(update_fields=["health_remaining"])
    response = HttpResponse(value)
    return trigger_client_event(response, "refresh_health_bar")


@login_required
def character_mana_change(request, pk: int):
    character = get_object_or_404(
        Character.objects.managed_by(request.user)
        .only("mana_remaining", "level", "value_intelligence", "profile")
        .select_related("profile"),
        pk=pk,
    )
    value = get_updated_value(request, character.mana_remaining, character.mana_max)
    character.mana_remaining = value
    character.save(update_fields=["mana_remaining"])
    response = HttpResponse(value)
    return trigger_client_event(response, "refresh_mana_bar")


@login_required
def character_recovery_points_change(request, pk: int):
    character = get_object_or_404(
        Character.objects.managed_by(request.user).only("recovery_points_remaining"),
        pk=pk,
    )
    value = get_updated_value(
        request, character.recovery_points_remaining, character.recovery_points_max
    )
    character.recovery_points_remaining = value
    character.save(update_fields=["recovery_points_remaining"])
    return HttpResponse(value)


@login_required
def character_defense_misc_change(request, pk: int):
    character = get_object_or_404(
        Character.objects.managed_by(request.user).only("defense_misc"), pk=pk
    )
    value = get_updated_value(request, character.defense_misc, float("inf"))
    character.defense_misc = value
    character.save(update_fields=["defense_misc"])
    response = HttpResponse(value)
    return trigger_client_event(response, "update_defense")


@login_required
def character_shield_change(request, pk: int):
    character = get_object_or_404(
        Character.objects.managed_by(request.user).only("shield"), pk=pk
    )
    value = get_updated_value(request, character.shield, float("inf"))
    character.shield = value
    character.save(update_fields=["shield"])
    response = HttpResponse(value)
    return trigger_client_event(response, "update_defense")


@login_required
def character_armor_change(request, pk: int):
    character = get_object_or_404(
        Character.objects.managed_by(request.user).only("armor"), pk=pk
    )
    value = get_updated_value(request, character.armor, float("inf"))
    character.armor = value
    character.save(update_fields=["armor"])
    response = HttpResponse(value)
    return trigger_client_event(response, "update_defense")


@login_required
def character_initiative_misc_change(request, pk: int):
    character = get_object_or_404(
        Character.objects.managed_by(request.user).only("initiative_misc"), pk=pk
    )
    value = get_updated_value(request, character.initiative_misc, float("inf"))
    character.initiative_misc = value
    character.save(update_fields=["initiative_misc"])
    response = HttpResponse(value)
    return trigger_client_event(response, "update_initiative")


@login_required
def character_luck_points_change(request, pk: int):
    character = get_object_or_404(
        Character.objects.managed_by(request.user).only(
            "luck_points_remaining", "value_charisma"
        ),
        pk=pk,
    )
    value = get_updated_value(
        request, character.luck_points_remaining, character.luck_points_max
    )
    character.luck_points_remaining = value
    character.save(update_fields=["luck_points_remaining"])
    return HttpResponse(value)


def get_updated_value(
    request, remaining_value: int | float, max_value: int | float
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
    return int(remaining_value)


@login_required
def character_get_defense(request, pk: int):
    character = get_object_or_404(
        Character.objects.managed_by(request.user).only(
            "defense_misc", "armor", "shield", "value_dexterity"
        ),
        pk=pk,
    )
    return HttpResponse(character.defense)


@login_required
def character_get_health_bar(request, pk: int):
    character = get_object_or_404(
        Character.objects.managed_by(request.user).only(
            "health_max", "health_remaining"
        ),
        pk=pk,
    )
    context = {"character": character}
    return render(
        request, "character/snippets/character_details/health_bar.html", context
    )


@login_required
def character_get_mana_bar(request, pk: int):
    character = get_object_or_404(
        Character.objects.managed_by(request.user).select_related("profile"),
        pk=pk,
    )
    context = {"character": character}
    return render(
        request, "character/snippets/character_details/mana_bar.html", context
    )


@login_required
def character_get_initiative(request, pk: int):
    character = get_object_or_404(
        Character.objects.managed_by(request.user).only(
            "initiative_misc", "value_dexterity"
        ),
        pk=pk,
    )
    return HttpResponse(modifier(character.modifier_initiative))


@login_required
def character_notes_change(request, pk: int):
    return update_text_field(request, pk, "notes")


@login_required
def character_gm_notes_change(request, pk: int):
    return update_text_field(request, pk, "gm_notes")


@login_required
def character_equipment_change(request, pk: int):
    field = "equipment"
    character = get_object_or_404(
        Character.objects.managed_by(request.user).only(field), pk=pk
    )
    context = {"character": character}
    if request.method == "GET":
        return render(
            request,
            f"character/snippets/character_details/{field}_update.html",
            context,
        )
    form = EquipmentForm(request.POST, instance=character)
    if form.is_valid():
        form.save()
        return render(
            request,
            f"character/snippets/character_details/{field}_display.html",
            context,
        )
    context["errors"] = form.errors
    return render(
        request,
        f"character/snippets/character_details/{field}_update.html",
        context,
    )


@login_required
def character_damage_reduction_change(request, pk: int):
    return update_text_field(request, pk, "damage_reduction")


def update_text_field(request, pk, field):
    character = get_object_or_404(
        Character.objects.managed_by(request.user).only(field), pk=pk
    )
    context = {"character": character}
    if request.method == "GET":
        return render(
            request,
            f"character/snippets/character_details/{field}_update.html",
            context,
        )
    setattr(character, field, request.POST.get(field))
    character.save(update_fields=[field])
    return render(
        request, f"character/snippets/character_details/{field}_display.html", context
    )


@login_required
def add_next_in_path(request, character_pk: int, path_pk: int):
    character = get_object_or_404(
        Character.objects.managed_by(request.user), pk=character_pk
    )
    path = get_object_or_404(Path, pk=path_pk)
    capability = path.get_next_capability(character)
    character.capabilities.add(capability)
    context = {
        "character": character,
        "add_path_form": AddPathForm(character),
    }
    return render(
        request,
        "character/snippets/character_details/paths_and_capabilities.html",
        context,
    )


@login_required
def remove_last_in_path(request, character_pk: int, path_pk: int):
    character = get_object_or_404(
        Character.objects.managed_by(request.user), pk=character_pk
    )
    last_rank = max(
        character.capabilities.filter(path_id=path_pk).values_list("rank", flat=True)
    )
    cap = Capability.objects.get(path_id=path_pk, rank=last_rank)
    character.capabilities.remove(cap)
    context = {
        "character": character,
        "add_path_form": AddPathForm(character),
    }
    return render(
        request,
        "character/snippets/character_details/paths_and_capabilities.html",
        context,
    )


@login_required
def remove_state(request, pk: int, state_pk: int):
    character: Character = get_object_or_404(
        Character.objects.managed_by(request.user), pk=pk
    )
    state = get_object_or_404(HarmfulState, pk=state_pk)
    character.states.remove(state)
    context = {"character": character, "all_states": HarmfulState.objects.all()}
    response = render(
        request, "character/snippets/character_details/states.html", context
    )
    return trigger_client_event(response, "refresh_tooltips", after="swap")


@login_required
def add_state(request, pk: int, state_pk: int):
    character: Character = get_object_or_404(
        Character.objects.managed_by(request.user), pk=pk
    )
    state = get_object_or_404(HarmfulState, pk=state_pk)
    character.states.add(state)
    context = {"character": character, "all_states": HarmfulState.objects.all()}
    response = render(
        request, "character/snippets/character_details/states.html", context
    )
    return trigger_client_event(response, "refresh_tooltips", after="swap")


@login_required
def reset_stats(request, pk: int):
    character: Character = get_object_or_404(
        Character.objects.managed_by(request.user), pk=pk
    )
    context = {"character": character}
    if request.method == "POST":
        character.reset_stats()
        messages.success(request, f"Les stats de {character} ont été réinitialisées.")
        return redirect(character)
    return render(request, "character/character_reset_stats.html", context)
