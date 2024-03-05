from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from character.models import Character, HarmfulState
from party.forms import BattleEffectForm, PartyForm
from party.models import BattleEffect, Party


@require_GET
@login_required
def parties_list(request):
    context = {
        "managed_parties": Party.objects.managed_by(request.user),
        "played_parties": Party.objects.played_by(request.user).distinct(),
        "invited_to": Party.objects.invited_to(request.user).distinct(),
    }
    return render(request, "party/parties_list.html", context)


@require_http_methods(["GET", "POST"])
@login_required
def party_create(request):
    if request.method == "GET":
        form = PartyForm()
    else:
        form = PartyForm(request.POST)
        if form.is_valid():
            party = form.save(commit=False)
            party.game_master = request.user
            party.save()
            form.save_m2m()
            return redirect("party:list")
    context = {"form": form}
    return render(request, "party/party_form.html", context)


@require_GET
@login_required
def party_details(request, pk):
    party = get_object_or_404(Party.objects.related_to(request.user), pk=pk)
    context = {
        "party": party,
        "all_states": HarmfulState.objects.all(),
    }
    return render(request, "party/party_details.html", context)


@require_http_methods(["GET", "POST"])
@login_required
def party_delete(request, pk):
    party = get_object_or_404(Party.objects.managed_by(request.user), pk=pk)
    context = {"party": party}
    if request.method == "POST":
        name = party.name
        party.delete()
        messages.success(request, f"Le groupe {name} a été supprimé.")
        return redirect("party:list")
    return render(request, "party/party_delete.html", context)


@require_http_methods(["GET", "POST"])
@login_required
def party_reset_stats(request, pk):
    party = get_object_or_404(Party.objects.managed_by(request.user), pk=pk)
    context = {"party": party}
    if request.method == "POST":
        name = party.name
        party.reset_stats()
        message = f"Les stats de tous les membres de {name} ont été réinitialisées."
        messages.success(request, message)
        return redirect(party)
    return render(request, "party/party_reset_stats.html", context)


@require_http_methods(["GET", "POST"])
@login_required
def party_add_effect(request, pk):
    party = get_object_or_404(Party.objects.played_or_mastered_by(request.user), pk=pk)
    context = {"party": party}
    if request.method == "GET":
        form = BattleEffectForm()
    else:
        form = BattleEffectForm(request.POST or None)
        if form.is_valid():
            effect = form.save(commit=False)
            effect.party = party
            effect.created_by = request.user
            effect.save()
            return render(request, "party/snippets/effects.html", context)
    context["form"] = form
    return render(request, "party/snippets/add_effect_form.html", context)


@require_GET
@login_required
def party_increase_rounds(request, pk):
    party = get_object_or_404(Party.objects.played_or_mastered_by(request.user), pk=pk)
    party.effects.increase_rounds()
    return render(request, "party/snippets/effects.html", {"party": party})


@require_GET
@login_required
def party_decrease_rounds(request, pk):
    party = get_object_or_404(Party.objects.played_or_mastered_by(request.user), pk=pk)
    party.effects.decrease_rounds()
    return render(request, "party/snippets/effects.html", {"party": party})


@require_GET
@login_required
def party_delete_effect(request, pk, effect_pk):
    party = get_object_or_404(Party.objects.played_or_mastered_by(request.user), pk=pk)
    BattleEffect.objects.filter(pk=effect_pk).delete()
    return render(request, "party/snippets/effects.html", {"party": party})


@require_http_methods(["GET", "POST"])
@login_required
def party_change(request, pk):
    party = get_object_or_404(Party.objects.managed_by(request.user), pk=pk)
    context = {"party": party}
    if request.method == "GET":
        form = PartyForm(instance=party)
    else:
        form = PartyForm(request.POST or None, instance=party)
        if form.is_valid():
            form.save()
            messages.success(request, "Groupe modifié.")
            return redirect("party:list")
    context["form"] = form
    return render(request, "party/party_form.html", context)


@require_http_methods(["GET", "POST"])
@login_required
def party_leave(request, pk, character_pk):
    party = get_object_or_404(Party.objects.played_by(request.user).distinct(), pk=pk)
    character = get_object_or_404(
        Character.objects.owned_by(request.user),
        pk=character_pk,
    )
    context = {"party": party, "character": character}
    if request.method == "POST":
        character.parties.remove(party)
        messages.success(request, f"{character} a quitté le groupe {party}.")
        return redirect("party:list")
    return render(request, "party/party_leave.html", context)


@require_GET
@login_required
def party_join(request, pk, character_pk):
    party = get_object_or_404(Party.objects.invited_to(request.user).distinct(), pk=pk)
    character = get_object_or_404(
        Character.objects.owned_by(request.user),
        pk=character_pk,
    )
    party.characters.add(character)
    party.invited_characters.remove(character)
    messages.success(request, f"{character} a rejoint le groupe {party}.")
    return redirect("party:list")


@require_GET
@login_required
def party_refuse(request, pk, character_pk):
    party = get_object_or_404(Party.objects.invited_to(request.user).distinct(), pk=pk)
    character = get_object_or_404(
        Character.objects.owned_by(request.user),
        pk=character_pk,
    )
    party.invited_characters.remove(character)
    messages.success(request, f"{character} a refusé l'invitation au groupe {party}.")
    return redirect("party:list")
