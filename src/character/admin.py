from django.contrib import admin
from django.forms import ModelForm

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


class CapabilityInline(admin.TabularInline):
    model = models.Capability
    fields = ["name", "rank", "limited", "spell"]


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
    inlines = [CapabilityInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("profile", "race")

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
        (
            None,
            {"fields": ["name", ("magical_strength", "life_dice", "mana_max_compute")]},
        ),
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


class CharacterAdminForm(ModelForm):
    class Meta:
        model = models.Character
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["capabilities"].queryset = models.Capability.objects.select_related(
            "path", "path__race", "path__profile"
        )
        self.fields[
            "racial_capability"
        ].queryset = models.RacialCapability.objects.select_related("race")


class PartyInline(admin.TabularInline):
    model = models.Character.parties.through
    extra = 0


@admin.register(models.Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ["name", "player", "race", "profile", "level"]
    list_filter = ["race", "profile"]
    search_fields = ["name", "notes"]

    fieldsets = [
        (
            "Identité",
            {"fields": ["name", "player", "profile", "level", "race", "private"]},
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
            {
                "fields": [
                    ("initiative_misc", "modifier_initiative"),
                    "attack_melee",
                    "attack_range",
                    "attack_magic",
                    "states",
                ]
            },
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
        "modifier_initiative",
        "attack_melee",
        "attack_range",
        "attack_magic",
        "defense",
        "mana_max",
        "recovery_points_max",
        "luck_points_max",
    ]
    filter_horizontal = [
        "capabilities",
        "weapons",
        "states",
    ]
    inlines = [PartyInline]

    form = CharacterAdminForm

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return super().has_change_permission(request, obj)
        return obj.player == request.user or request.user.is_superuser


@admin.register(models.Weapon)
class WeaponAdmin(admin.ModelAdmin):
    list_display = ["name", "damage"]
    search_fields = ["name", "special", "damage"]


@admin.register(models.HarmfulState)
class HarmfulStateAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]
