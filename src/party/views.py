from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

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
