from django.urls import path

from character import views

app_name = "character"
urlpatterns = [
    path("", views.characters_list, name="list"),
    path("create/", views.character_create, name="create"),
    path("<int:pk>/", views.character_view, name="view"),
    path(
        "<int:pk>/health_change/", views.character_health_change, name="health_change"
    ),
    path("<int:pk>/mana_change/", views.character_mana_change, name="mana_change"),
    path(
        "<int:pk>/recovery_points_change/",
        views.character_recovery_points_change,
        name="recovery_points_change",
    ),
    path(
        "<int:pk>/luck_points_change/",
        views.character_luck_points_change,
        name="luck_points_change",
    ),
    path("<int:pk>/notes_change/", views.character_notes_change, name="notes_change"),
    path("<int:pk>/get_defense/", views.character_get_defense, name="get_defense"),
    path(
        "<int:pk>/defense_misc_change/",
        views.character_defense_misc_change,
        name="defense_misc_change",
    ),
    path(
        "<int:pk>/shield_change/",
        views.character_shield_change,
        name="shield_change",
    ),
    path(
        "<int:pk>/armor_change/",
        views.character_armor_change,
        name="armor_change",
    ),
    path(
        "<int:pk>/get_initiative/",
        views.character_get_initiative,
        name="get_initiative",
    ),
    path(
        "<int:pk>/initiative_misc_change/",
        views.character_initiative_misc_change,
        name="initiative_misc_change",
    ),
    path(
        "<int:pk>/equipment_change/",
        views.character_equipment_change,
        name="equipment_change",
    ),
    path(
        "<int:pk>/damage_reduction_change/",
        views.character_damage_reduction_change,
        name="damage_reduction_change",
    ),
    path(
        "<int:character_pk>/add_next_in_path/<int:path_pk>/",
        views.add_next_in_path,
        name="add_next_in_path",
    ),
    path(
        "<int:character_pk>/remove_last_in_path/<int:path_pk>/",
        views.remove_last_in_path,
        name="remove_last_in_path",
    ),
    path("<int:pk>/add_path/", views.add_path, name="add_path"),
    path(
        "<int:pk>/remove_state/<int:state_pk>/", views.remove_state, name="remove_state"
    ),
]
