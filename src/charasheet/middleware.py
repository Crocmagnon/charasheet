from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse


def debug_toolbar_bypass_internal_ips(_) -> bool:
    """
    Display debug toolbar according to the DEBUG_TOOLBAR setting only.

    By default, DjDT is displayed according to an `INTERNAL_IPS` settings.
    This is impossible to predict in a docker/k8s environment so we bypass this check.
    """
    return settings.DEBUG_TOOLBAR


class PreviewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: WSGIRequest):
        enable_preview = "enable_preview" in request.GET
        disable_preview = "disable_preview" in request.GET

        new_value = None

        if enable_preview:
            new_value = True
        elif disable_preview:
            new_value = False

        if new_value is not None:
            request.session["preview"] = new_value

        response: HttpResponse = self.get_response(request)

        if new_value is True:
            response.set_cookie("preview", "enabled")
        elif new_value is False:
            response.delete_cookie("preview")

        return response
