"""charasheet URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import logout
from django.urls import include, path
from django.views.generic import TemplateView
from django_registration.backends.activation.views import RegistrationView

from common.forms import RegistrationForm
from common.views import ActivationView, hello_world

urlpatterns = [
    path("logout/", logout, {"next_page": settings.LOGOUT_REDIRECT_URL}, name="logout"),
    path(
        "accounts/register/",
        RegistrationView.as_view(form_class=RegistrationForm),
        name="django_registration_register",
    ),
    path(
        "accounts/activate/complete/",
        TemplateView.as_view(
            template_name="django_registration/activation_complete.html"
        ),
        name="django_registration_activation_complete",
    ),
    path(
        "accounts/activate/<str:activation_key>/",
        ActivationView.as_view(),
        name="django_registration_activate",
    ),
    path("accounts/", include("django_registration.backends.activation.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("", hello_world, name="hello_world"),
    path("character/", include("character.urls", namespace="character")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG_TOOLBAR:
    urlpatterns.insert(0, path("__debug__/", include("debug_toolbar.urls")))

if settings.DEBUG:
    urlpatterns.insert(0, path("__reload__/", include("django_browser_reload.urls")))
