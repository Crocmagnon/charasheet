from django.contrib.auth.models import Permission
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django_registration.backends.activation.views import (
    ActivationView as BaseActivationView,
)


def hello_world(request: WSGIRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("character:list")
    return render(request, "common/hello.html")


class ActivationView(BaseActivationView):
    def activate(self, *args, **kwargs):
        user = super().activate(*args, **kwargs)
        perm = Permission.objects.get(
            content_type__app_label="character",
            content_type__model="character",
            codename="add_character",
        )
        user.user_permissions.add(perm)
        user.is_staff = True
        user.save()
        return user
