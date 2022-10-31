from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect


def hello_world(request: WSGIRequest) -> HttpResponse:
    return redirect("character:list")
