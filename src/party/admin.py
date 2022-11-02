from django.contrib import admin

from party import models


@admin.register(models.Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ["name", "game_master"]
    search_fields = ["name"]
