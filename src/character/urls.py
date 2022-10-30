from django.urls import path

from character import views

app_name = "character"
urlpatterns = [
    path("<int:pk>/", views.character_view, name="view"),
    path("<int:pk>/health_change", views.character_health_change, name="health_change"),
    path("<int:pk>/mana_change", views.character_mana_change, name="mana_change"),
]
