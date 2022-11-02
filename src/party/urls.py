from django.urls import path

from party import views

app_name = "party"
urlpatterns = [
    path("", views.parties_list, name="list"),
    path("create/", views.party_create, name="create"),
    path("<int:pk>/", views.party_details, name="details"),
]
