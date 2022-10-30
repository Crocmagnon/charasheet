from django.contrib import admin

from character import models


@admin.register(models.Capability)
class CapabilityAdmin(admin.ModelAdmin):
    list_display = ["name", "path", "rank", "limited", "spell"]
    list_filter = ["path", "path__profile", "path__race", "rank", "limited", "spell"]
    search_fields = ["name", "description"]
    fieldsets = [
        (None, {"fields": ["name"]}),
        ("Voie", {"fields": [("path", "rank")]}),
        ("Type", {"fields": [("limited", "spell")]}),
        ("Description", {"fields": ["description"]}),
        ("Documentation", {"fields": ["url"]}),
    ]


@admin.register(models.Path)
class PathAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "related_to"]
    list_filter = ["category"]
    search_fields = ["name"]
    fieldsets = [
        (None, {"fields": ["name"]}),
        ("Lié à", {"fields": ["category", ("profile", "race")]}),
        ("Notes", {"fields": ["notes"]}),
        ("Documentation", {"fields": ["url"]}),
    ]

    def related_to(self, instance: models.Path) -> str:
        category = models.Path.Category(instance.category)
        if category == models.Path.Category.PROFILE:
            return str(instance.profile)
        elif category == models.Path.Category.RACE:
            return str(instance.race)
        else:
            return ""


@admin.register(models.RacialCapability)
class RacialCapabilityAdmin(admin.ModelAdmin):
    list_display = ["name", "race"]
    list_filter = ["race"]
    search_fields = ["name", "description"]


class PathInline(admin.TabularInline):
    model = models.Path
    fields = ["name"]
    extra = 0


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["name", "life_dice", "magical_strength"]
    list_filter = ["life_dice", "magical_strength"]
    search_fields = ["name"]
    inlines = [PathInline]
    fieldsets = [
        (None, {"fields": ["name", ("magical_strength", "life_dice")]}),
        ("Notes", {"fields": ["notes"]}),
        ("Documentation", {"fields": ["url"]}),
    ]


class RacialCapabilityInline(admin.TabularInline):
    model = models.RacialCapability
    extra = 0


@admin.register(models.Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    inlines = [RacialCapabilityInline, PathInline]


@admin.register(models.Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ["name", "player", "race", "profile", "level"]
    list_filter = ["race", "profile"]
    search_fields = ["name", "notes"]

    fieldsets = [
        (
            "Identité",
            {"fields": ["name", "player", "profile", "level", "race"]},
        ),
        ("Apparence", {"fields": ["gender", "age", "height", "weight"]}),
        (
            "Caractéristiques",
            {
                "fields": [
                    ("value_strength", "modifier_strength"),
                    ("value_dexterity", "modifier_dexterity"),
                    ("value_constitution", "modifier_constitution"),
                    ("value_intelligence", "modifier_intelligence"),
                    ("value_wisdom", "modifier_wisdom"),
                    ("value_charisma", "modifier_charisma"),
                ]
            },
        ),
        (
            "Combat",
            {"fields": ["initiative", "attack_melee", "attack_range", "attack_magic"]},
        ),
        ("Vitalité", {"fields": [("health_max", "health_remaining")]}),
        ("Défense", {"fields": ["armor", "shield", "defense_misc", "defense"]}),
        (
            "Armes & équipement",
            {
                "fields": [
                    "weapons",
                    "equipment",
                    ("money_pp", "money_po", "money_pa", "money_pc"),
                ]
            },
        ),
        ("Race", {"fields": ["racial_capability"]}),
        ("Capacités", {"fields": ["capabilities"]}),
        ("Chance", {"fields": [("luck_points_max", "luck_points_remaining")]}),
        ("Mana", {"fields": [("mana_max", "mana_remaining")]}),
        (
            "Récupération",
            {"fields": [("recovery_points_max", "recovery_points_remaining")]},
        ),
        ("Notes", {"fields": ["notes"]}),
    ]
    readonly_fields = [
        "modifier_strength",
        "modifier_dexterity",
        "modifier_constitution",
        "modifier_intelligence",
        "modifier_wisdom",
        "modifier_charisma",
        "initiative",
        "attack_melee",
        "attack_range",
        "attack_magic",
        "defense",
        "mana_max",
        "recovery_points_max",
    ]
    filter_horizontal = [
        "capabilities",
        "weapons",
    ]


@admin.register(models.Weapon)
class WeaponAdmin(admin.ModelAdmin):
    list_display = ["name", "damage"]
    search_fields = ["name", "special", "damage"]
