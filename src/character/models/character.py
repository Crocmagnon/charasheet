import collections
from collections.abc import Iterable
from dataclasses import dataclass
from functools import partial

import markdown
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel

from character.models import Capability, Path
from character.models.dice import Dice
from character.models.equipment import Weapon
from character.models.utils import cache_on_instance
from common.models import DocumentedModel, UniquelyNamedModel


class Profile(  # noqa: DJ008
    DocumentedModel,
    UniquelyNamedModel,
    TimeStampedModel,
    models.Model,
):
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
        choices=Dice.choices,
        verbose_name="dé de vie",
    )
    mana_max_compute = models.PositiveSmallIntegerField(
        choices=ManaMax.choices,
        verbose_name="calcul mana max",
        default=ManaMax.NO_MANA,
    )
    notes = models.TextField(blank=True, verbose_name="notes")

    class Meta(UniquelyNamedModel.Meta, TimeStampedModel.Meta):
        verbose_name = "Profil"
        verbose_name_plural = "Profils"


class Race(  # noqa: DJ008
    DocumentedModel,
    UniquelyNamedModel,
    TimeStampedModel,
    models.Model,
):
    class Meta(UniquelyNamedModel.Meta, TimeStampedModel.Meta):
        verbose_name = "Race"
        verbose_name_plural = "Races"


class HarmfulState(  # noqa: DJ008
    DocumentedModel,
    UniquelyNamedModel,
    TimeStampedModel,
    models.Model,
):
    description = models.TextField()
    icon_url = models.URLField()

    class Meta(UniquelyNamedModel.Meta, TimeStampedModel.Meta):
        verbose_name = "État préjudiciable"
        verbose_name_plural = "États préjudiciables"


def modifier(value: int) -> int:
    if not value:
        return 0
    if 1 < value < 10:  # noqa: PLR2004
        value -= 1
    value -= 10
    return int(value / 2)


class CharacterManager(models.Manager):
    def get_by_natural_key(self, name: str, player_id: int):
        return self.get(name=name, player_id=player_id)


class CharacterQuerySet(models.QuerySet):
    def managed_by(self, user):
        """
        Return characters managed by the given user.

        Characters are managed by a user if they own the character
        or if they are the game master for a group in which the character plays.
        """
        from party.models import Party

        return self.filter(
            Q(player=user) | Q(parties__in=Party.objects.managed_by(user)),
        )

    def mastered_by(self, user):
        """Return characters in groups where the given user is the game master."""
        from party.models import Party

        return self.filter(parties__in=Party.objects.managed_by(user))

    def owned_by(self, user):
        """Return characters either owned by the given user."""
        return self.filter(player=user)

    def friendly_to(self, user):
        """
        Return characters friendly to the given users.

        Friendly characters are either owned by the given user
        or in a party related to the given user.
        """
        from party.models import Party

        return self.filter(
            Q(player=user)
            | Q(parties__in=Party.objects.related_to(user))
            | Q(invites__in=Party.objects.related_to(user)),
        ).distinct()


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


def validate_image(fieldfile_obj, megabytes_limit: float):
    filesize = fieldfile_obj.file.size
    if filesize > megabytes_limit * 1024 * 1024:
        msg = f"La taille maximale est de {megabytes_limit}Mo"
        raise ValidationError(msg)


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
    profile_picture = models.ImageField(
        verbose_name="image de profil",
        upload_to="profile_pictures",
        blank=True,
        null=True,
        validators=[partial(validate_image, megabytes_limit=2)],
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
        max_length=1,
        choices=Gender.choices,
        default=Gender.OTHER,
        verbose_name="genre",
    )
    age = models.PositiveSmallIntegerField(verbose_name="âge")
    height = models.PositiveSmallIntegerField(verbose_name="taille")
    weight = models.PositiveSmallIntegerField(verbose_name="poids")

    value_strength = models.PositiveSmallIntegerField(verbose_name="valeur force")
    value_dexterity = models.PositiveSmallIntegerField(verbose_name="valeur dextérité")
    value_constitution = models.PositiveSmallIntegerField(
        verbose_name="valeur constitution",
    )
    value_intelligence = models.PositiveSmallIntegerField(
        verbose_name="valeur intelligence",
    )
    value_wisdom = models.PositiveSmallIntegerField(verbose_name="valeur sagesse")
    value_charisma = models.PositiveSmallIntegerField(verbose_name="valeur charisme")

    bonus_strength = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="bonus force",
    )
    bonus_dexterity = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="bonus dextérité",
    )
    bonus_constitution = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="bonus constitution",
    )
    bonus_intelligence = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="bonus intelligence",
    )
    bonus_wisdom = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="bonus sagesse",
    )
    bonus_charisma = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="bonus charisme",
    )

    health_max = models.PositiveSmallIntegerField(verbose_name="points de vie max")
    health_remaining = models.PositiveSmallIntegerField(
        verbose_name="points de vie restants",
    )

    racial_capability = models.ForeignKey(
        "character.RacialCapability",
        on_delete=models.PROTECT,
        related_name="characters",
        verbose_name="capacité raciale",
    )

    weapons = models.ManyToManyField(
        "character.Weapon",
        blank=True,
        verbose_name="armes",
    )

    armor = models.PositiveSmallIntegerField(verbose_name="armure", default=0)
    shield = models.PositiveSmallIntegerField(verbose_name="bouclier", default=0)
    defense_misc = models.SmallIntegerField(verbose_name="divers défense", default=0)

    initiative_misc = models.SmallIntegerField(
        verbose_name="divers initiative",
        default=0,
    )

    capabilities = models.ManyToManyField(
        "character.Capability",
        blank=True,
        verbose_name="capacités",
    )
    paths = models.ManyToManyField("character.Path", blank=True, verbose_name="voies")

    equipment = models.TextField(blank=True, verbose_name="équipement")
    luck_points_remaining = models.PositiveSmallIntegerField(
        verbose_name="points de chance restants",
    )

    mana_remaining = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="mana restant",
    )

    money_pp = models.PositiveSmallIntegerField(default=0, verbose_name="PP")
    money_po = models.PositiveSmallIntegerField(default=0, verbose_name="PO")
    money_pa = models.PositiveSmallIntegerField(default=0, verbose_name="PA")
    money_pc = models.PositiveSmallIntegerField(default=0, verbose_name="PC")

    recovery_points_remaining = models.PositiveSmallIntegerField(
        default=5,
        verbose_name="points de récupération restants",
    )

    notes = models.TextField(blank=True, verbose_name="notes", default=DEFAULT_NOTES)
    gm_notes = models.TextField(blank=True, verbose_name="notes MJ")
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
                Lower("name"),
                "player",
                name="unique_character_player",
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("character:view", kwargs={"pk": self.pk})

    def natural_key(self):
        return (self.name, self.player_id)

    @property
    def modifier_strength(self) -> int:
        return modifier(self.value_strength) + self.bonus_strength

    @property
    def modifier_dexterity(self) -> int:
        return modifier(self.value_dexterity) + self.bonus_dexterity

    @property
    def modifier_constitution(self) -> int:
        return modifier(self.value_constitution) + self.bonus_constitution

    @property
    def modifier_intelligence(self) -> int:
        return modifier(self.value_intelligence) + self.bonus_intelligence

    @property
    def modifier_wisdom(self) -> int:
        return modifier(self.value_wisdom) + self.bonus_wisdom

    @property
    def modifier_charisma(self) -> int:
        return modifier(self.value_charisma) + self.bonus_charisma

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
            Profile.MagicalStrength(self.profile.magical_strength),
            0,
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
        if mana_max_compute == Profile.ManaMax.LEVEL:
            return self.level + self.modifier_magic
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
        return max([3 + self.modifier_charisma, 0])

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

    @property
    def capability_points_max(self) -> int:
        return 2 * self.level

    @property
    def capability_points_used(self) -> int:
        return sum(
            cap.capability_points_cost
            for cap in self.capabilities.select_related("path").only(
                "rank",
                "path__category",
            )
        )

    @property
    def capability_points_remaining(self) -> int:
        return self.capability_points_max - self.capability_points_used

    def get_modifier_for_weapon(self, weapon: Weapon) -> int:
        modifier_map = {
            Weapon.Category.RANGE: self.modifier_dexterity,
            Weapon.Category.MELEE: self.modifier_strength,
            Weapon.Category.NONE: 0,
        }
        return modifier_map.get(Weapon.Category(weapon.category), 0) + self.level

    def get_capabilities_by_path(self) -> dict[Path, list[CharacterCapability]]:
        capabilities_by_path = collections.defaultdict(list)
        character_capabilities = set(self.capabilities.all())
        character_paths = {
            capability.path for capability in character_capabilities
        } | set(self.paths.all())
        for path in character_paths:
            for capability in path.capabilities.all():
                capabilities_by_path[capability.path].append(
                    CharacterCapability(
                        capability,
                        known=capability in character_capabilities,
                    ),
                )

        return dict(
            sorted(
                (
                    (path, sorted(capabilities, key=lambda x: x.capability.rank))
                    for path, capabilities in capabilities_by_path.items()
                ),
                key=lambda x: x[0].name,
            ),
        )

    def get_formatted_notes(self) -> str:
        md = markdown.Markdown(extensions=["extra", "nl2br"])
        return md.convert(self.notes)

    def get_formatted_gm_notes(self) -> str:
        md = markdown.Markdown(extensions=["extra", "nl2br"])
        return md.convert(self.gm_notes)

    def get_missing_states(self) -> Iterable[HarmfulState]:
        return HarmfulState.objects.exclude(
            pk__in=self.states.all().values_list("pk", flat=True),
        )

    @cache_on_instance()
    def managed_by(self, user):
        return self in Character.objects.managed_by(user)

    @cache_on_instance()
    def mastered_by(self, user):
        return self in Character.objects.mastered_by(user)

    @cache_on_instance()
    def owned_by(self, user):
        return self in Character.objects.owned_by(user)

    def reset_stats(self):
        self.health_remaining = self.health_max
        self.mana_remaining = self.mana_max
        self.luck_points_remaining = self.luck_points_max
        self.recovery_points_remaining = self.recovery_points_max
        self.save()
