from django.urls import path

from character import views

app_name = "character"
urlpatterns = [path("<int:pk>/", views.character_view, name="view")]
