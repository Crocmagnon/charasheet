from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from character.models import Character


@login_required
def character_view(request: WSGIRequest, pk: int) -> HttpResponse:
    character = get_object_or_404(Character, pk=pk)
    context = {"character": character}
    return render(request, "character/view.html", context)
