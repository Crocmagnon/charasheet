from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render


def hello_world(request: WSGIRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("character:list")
    return render(request, "common/hello.html")
