import collections
from collections.abc import Iterable
from dataclasses import dataclass

import markdown
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel

from character.models import Capability, Path
from character.models.dice import Dice
from character.models.equipment import Weapon
from common.models import DocumentedModel, UniquelyNamedModel


class Profile(DocumentedModel, UniquelyNamedModel, TimeStampedModel, models.Model):
    class MagicalStrength(models.TextChoices):
        NONE = "NON", "Aucun"
        INTELLIGENCE = "INT", "Intelligence"
        WISDOM = "SAG", "Sagesse"
        CHARISMA = "CHA", "Charisme"

    class ManaMax(models.IntegerChoices):
        NO_MANA = 0, "Pas de mana"
        LEVEL = 1, "1 x niveau + mod. magique"
        DOUBLE_LEVEL = 2, "2 x niveau + mod. magique"

    magical_strength = models.CharField(
        max_length=3,
        choices=MagicalStrength.choices,
        default=MagicalStrength.NONE,
        verbose_name="force magique",
    )
    life_dice = models.PositiveSmallIntegerField(
        choices=Dice.choices, verbose_name="dé de vie"
    )
    mana_max_compute = models.PositiveSmallIntegerField(
        choices=ManaMax.choices, verbose_name="calcul mana max", default=ManaMax.NO_MANA
    )
    notes = models.TextField(blank=True, verbose_name="notes")

    class Meta(UniquelyNamedModel.Meta, TimeStampedModel.Meta):
        verbose_name = "Profil"
        verbose_name_plural = "Profils"


class Race(DocumentedModel, UniquelyNamedModel, TimeStampedModel, models.Model):
    class Meta(UniquelyNamedModel.Meta, TimeStampedModel.Meta):
        verbose_name = "Race"
        verbose_name_plural = "Races"


class HarmfulState(DocumentedModel, UniquelyNamedModel, TimeStampedModel, models.Model):
    description = models.TextField()
    icon_url = models.URLField()

    class Meta(UniquelyNamedModel.Meta, TimeStampedModel.Meta):
        verbose_name = "État préjudiciable"
        verbose_name_plural = "États préjudiciables"


def modifier(value: int) -> int:
    if not value:
        return 0
    if 1 < value < 10:
        value -= 1
    value -= 10
    return int(value / 2)


class CharacterManager(models.Manager):
    def get_by_natural_key(self, name: str, player_id: int):
        return self.get(name=name, player_id=player_id)


class CharacterQuerySet(models.QuerySet):
    def managed_by(self, user):
        from party.models import Party

        return self.filter(
            Q(player=user) | Q(parties__in=Party.objects.managed_by(user))
        )

    def owned_by(self, user):
        return self.filter(player=user)


DEFAULT_NOTES = """
#### Traits personnalisés

#### Objectifs

#### Langages

#### Historique

#### Handicaps

#### Alignement

#### Relations

#### Religion
""".lstrip()


@dataclass
class CharacterCapability:
    capability: Capability
    known: bool = False


class Character(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Mâle"
        FEMALE = "F", "Femelle"
        OTHER = "O", "Autre"

    name = models.CharField(max_length=100, verbose_name="nom")
    player = models.ForeignKey(
        "common.User",
        on_delete=models.CASCADE,
        related_name="characters",
        verbose_name="joueur",
    )

    race = models.ForeignKey(
        "character.Race",
        on_delete=models.PROTECT,
        related_name="characters",
        verbose_name="race",
    )
    profile = models.ForeignKey(
        "character.Profile",
        on_delete=models.PROTECT,
        related_name="characters",
        verbose_name="profil",
    )
    level = models.PositiveSmallIntegerField(verbose_name="niveau", default=1)

    gender = models.CharField(
        max_length=1, choices=Gender.choices, default=Gender.OTHER, verbose_name="genre"
    )
    age = models.PositiveSmallIntegerField(verbose_name="âge")
    height = models.PositiveSmallIntegerField(verbose_name="taille")
    weight = models.PositiveSmallIntegerField(verbose_name="poids")

    value_strength = models.PositiveSmallIntegerField(verbose_name="valeur force")
    value_dexterity = models.PositiveSmallIntegerField(verbose_name="valeur dextérité")
    value_constitution = models.PositiveSmallIntegerField(
        verbose_name="valeur constitution"
    )
    value_intelligence = models.PositiveSmallIntegerField(
        verbose_name="valeur intelligence"
    )
    value_wisdom = models.PositiveSmallIntegerField(verbose_name="valeur sagesse")
    value_charisma = models.PositiveSmallIntegerField(verbose_name="valeur charisme")

    health_max = models.PositiveSmallIntegerField(verbose_name="points de vie max")
    health_remaining = models.PositiveSmallIntegerField(
        verbose_name="points de vie restants"
    )

    racial_capability = models.ForeignKey(
        "character.RacialCapability",
        on_delete=models.PROTECT,
        related_name="characters",
        verbose_name="capacité raciale",
    )

    weapons = models.ManyToManyField(
        "character.Weapon", blank=True, verbose_name="armes"
    )

    armor = models.PositiveSmallIntegerField(verbose_name="armure", default=0)
    shield = models.PositiveSmallIntegerField(verbose_name="bouclier", default=0)
    defense_misc = models.SmallIntegerField(verbose_name="divers défense", default=0)

    initiative_misc = models.SmallIntegerField(
        verbose_name="divers initiative", default=0
    )

    capabilities = models.ManyToManyField(
        "character.Capability", blank=True, verbose_name="capacités"
    )

    equipment = models.TextField(blank=True, verbose_name="équipement")
    luck_points_remaining = models.PositiveSmallIntegerField(
        verbose_name="points de chance restants"
    )

    mana_remaining = models.PositiveSmallIntegerField(
        default=0, verbose_name="mana restant"
    )

    money_pp = models.PositiveSmallIntegerField(default=0, verbose_name="PP")
    money_po = models.PositiveSmallIntegerField(default=0, verbose_name="PO")
    money_pa = models.PositiveSmallIntegerField(default=0, verbose_name="PA")
    money_pc = models.PositiveSmallIntegerField(default=0, verbose_name="PC")

    recovery_points_remaining = models.PositiveSmallIntegerField(
        default=5, verbose_name="points de récupération restants"
    )

    notes = models.TextField(blank=True, verbose_name="notes", default=DEFAULT_NOTES)
    damage_reduction = models.TextField(blank=True, verbose_name="réduction de dégâts")

    states = models.ManyToManyField(HarmfulState, blank=True, related_name="characters")

    private = models.BooleanField(
        "privé",
        help_text="Empêche toute invitation dans un groupe.",
        default=False,
        blank=True,
    )

    objects = CharacterManager.from_queryset(CharacterQuerySet)()

    class Meta:
        verbose_name = "Personnage"
        verbose_name_plural = "Personnages"
        constraints = [
            models.UniqueConstraint(
                Lower("name"), "player", name="unique_character_player"
            )
        ]

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name, self.player_id)

    def get_absolute_url(self):
        return reverse("character:view", kwargs={"pk": self.pk})

    @property
    def modifier_strength(self) -> int:
        return modifier(self.value_strength)

    @property
    def modifier_dexterity(self) -> int:
        return modifier(self.value_dexterity)

    @property
    def modifier_constitution(self) -> int:
        return modifier(self.value_constitution)

    @property
    def modifier_intelligence(self) -> int:
        return modifier(self.value_intelligence)

    @property
    def modifier_wisdom(self) -> int:
        return modifier(self.value_wisdom)

    @property
    def modifier_charisma(self) -> int:
        return modifier(self.value_charisma)

    @property
    def modifier_initiative(self) -> int:
        return self.modifier_dexterity + self.initiative_misc

    @property
    def attack_melee(self) -> int:
        return self.level + self.modifier_strength

    @property
    def attack_range(self) -> int:
        return self.level + self.modifier_dexterity

    @property
    def attack_magic(self) -> int:
        return self.level + self.modifier_magic

    @property
    def modifier_magic(self) -> int:
        modifier_map = {
            Profile.MagicalStrength.INTELLIGENCE: self.modifier_intelligence,
            Profile.MagicalStrength.WISDOM: self.modifier_wisdom,
            Profile.MagicalStrength.CHARISMA: self.modifier_charisma,
            Profile.MagicalStrength.NONE: 0,
        }
        return modifier_map.get(
            Profile.MagicalStrength(self.profile.magical_strength), 0
        )

    @property
    def defense(self) -> int:
        return (
            10 + self.armor + self.shield + self.modifier_dexterity + self.defense_misc
        )

    @property
    def mana_max(self) -> int:
        mana_max_compute = self.profile.mana_max_compute
        if mana_max_compute == Profile.ManaMax.NO_MANA:
            return 0
        elif mana_max_compute == Profile.ManaMax.LEVEL:
            return self.level + self.modifier_magic
        else:
            return 2 * self.level + self.modifier_magic

    @property
    def height_m(self) -> float:
        return round(self.height / 100, 2)

    @property
    def imc(self) -> float:
        return self.weight / (self.height_m**2)

    @property
    def recovery_points_max(self) -> int:
        return 5

    @property
    def luck_points_max(self) -> int:
        return 3 + self.modifier_charisma

    @property
    def health_remaining_percent(self) -> float:
        if self.health_max == 0:
            return 0
        return self.health_remaining / self.health_max * 100

    @property
    def mana_remaining_percent(self) -> float:
        if self.mana_max == 0:
            return 0
        return self.mana_remaining / self.mana_max * 100

    def get_modifier_for_weapon(self, weapon: Weapon) -> int:
        modifier_map = {
            Weapon.Category.RANGE: self.modifier_dexterity,
            Weapon.Category.MELEE: self.modifier_strength,
            Weapon.Category.NONE: 0,
        }
        return modifier_map.get(Weapon.Category(weapon.category), 0) + self.level

    def get_capabilities_by_path(self) -> dict[Path, list[CharacterCapability]]:
        capabilities_by_path = collections.defaultdict(list)
        character_capabilities = self.capabilities.all()
        character_paths = {capability.path for capability in character_capabilities}
        for path in character_paths:
            for capability in path.capabilities.all():
                capabilities_by_path[capability.path].append(
                    CharacterCapability(
                        capability, known=capability in character_capabilities
                    )
                )

        return dict(
            sorted(
                (
                    (path, sorted(capabilities, key=lambda x: x.capability.rank))
                    for path, capabilities in capabilities_by_path.items()
                ),
                key=lambda x: x[0].name,
            )
        )

    def get_formatted_notes(self) -> str:
        md = markdown.Markdown(extensions=["extra", "nl2br"])
        return md.convert(self.notes)

    def get_missing_states(self) -> Iterable[HarmfulState]:
        return HarmfulState.objects.exclude(
            pk__in=self.states.all().values_list("pk", flat=True)
        )

    def managed_by(self, user):
        return self in Character.objects.managed_by(user)
