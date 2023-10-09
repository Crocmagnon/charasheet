from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest


def app(_):
    return settings.APP


def preview(request: WSGIRequest):
    return {
        "preview_enabled": request.session.get("preview", False),
    }
