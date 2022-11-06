from django.urls import path

from party import views

app_name = "party"
urlpatterns = [
    path("", views.parties_list, name="list"),
    path("create/", views.party_create, name="create"),
    path("<int:pk>/", views.party_details, name="details"),
    path("<int:pk>/change/", views.party_change, name="change"),
    path("<int:pk>/delete/", views.party_delete, name="delete"),
    path("<int:pk>/leave/<int:character_pk>/", views.party_leave, name="leave"),
]
