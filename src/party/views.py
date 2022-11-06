from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from character.models import Character
from party.forms import PartyForm
from party.models import Party


@login_required
def parties_list(request):
    context = {
        "managed_parties": Party.objects.managed_by(request.user),
        "played_parties": Party.objects.played_by(request.user),
    }
    return render(request, "party/parties_list.html", context)


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
    return render(request, "party/party_create.html", context)


@login_required
def party_details(request, pk):
    party = get_object_or_404(Party.objects.related_to(request.user), pk=pk)
    context = {"party": party}
    return render(request, "party/party_details.html", context)


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


@login_required
def party_leave(request, pk, character_pk):
    party = get_object_or_404(Party.objects.managed_by(request.user), pk=pk)
    character = get_object_or_404(
        Character.objects.owned_by(request.user), pk=character_pk
    )
    context = {"party": party, "character": character}
    if request.method == "POST":
        character.parties.remove(party)
        messages.success(request, f"{character} a quitté le groupe {party}.")
        return redirect("party:list")
    return render(request, "party/party_leave.html", context)
