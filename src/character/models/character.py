from django.db import models
from django.db.models.functions import Lower
from django_extensions.db.models import TimeStampedModel

from character.models.dice import Dice
from common.models import UniquelyNamedModel


class Profile(UniquelyNamedModel, TimeStampedModel, models.Model):
    class MagicalStrength(models.TextChoices):
        NONE = "NON", "None"
        INTELLIGENCE = "INT", "Intelligence"
        WISDOM = "SAG", "Wisdom"
        CHARISMA = "CHA", "Charisma"

    magical_strength = models.CharField(
        max_length=3, choices=MagicalStrength.choices, default=MagicalStrength.NONE
    )
    life_dice = models.PositiveSmallIntegerField(choices=Dice.choices)
    notes = models.TextField(blank=True)


class Race(UniquelyNamedModel, TimeStampedModel, models.Model):
    pass


def modifier(value: int) -> int:
    if 1 < value < 10:
        value -= 1
    value -= 10
    return int(value / 2)


class CharacterManager(models.Manager):
    def get_by_natural_key(self, name: str, player_id: int):
        return self.get(name=name, player_id=player_id)


class Character(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    name = models.CharField(max_length=100)
    player = models.ForeignKey(
        "common.User", on_delete=models.CASCADE, related_name="characters"
    )

    race = models.ForeignKey(
        "character.Race",
        on_delete=models.PROTECT,
        related_name="characters",
    )
    profile = models.ForeignKey(
        "character.Profile",
        on_delete=models.PROTECT,
        related_name="characters",
    )
    level = models.PositiveSmallIntegerField()

    gender = models.CharField(
        max_length=1, choices=Gender.choices, default=Gender.OTHER
    )
    age = models.PositiveSmallIntegerField()
    height = models.PositiveSmallIntegerField()
    weight = models.PositiveSmallIntegerField()

    value_strength = models.PositiveSmallIntegerField()
    value_dexterity = models.PositiveSmallIntegerField()
    value_constitution = models.PositiveSmallIntegerField()
    value_intelligence = models.PositiveSmallIntegerField()
    value_wisdom = models.PositiveSmallIntegerField()
    value_charisma = models.PositiveSmallIntegerField()

    health_max = models.PositiveSmallIntegerField()
    health_remaining = models.PositiveSmallIntegerField()

    racial_capability = models.ForeignKey(
        "character.RacialCapability",
        on_delete=models.PROTECT,
        related_name="characters",
    )

    weapons = models.ManyToManyField("character.Weapon", blank=True)

    armor = models.PositiveSmallIntegerField()
    shield = models.PositiveSmallIntegerField()
    defense_misc = models.SmallIntegerField()

    capabilities = models.ManyToManyField("character.Capability", blank=True)

    equipment = models.TextField(blank=True)
    luck_points_max = models.PositiveSmallIntegerField()
    luck_points_remaining = models.PositiveSmallIntegerField()

    mana_consumed = models.PositiveSmallIntegerField(default=0)

    notes = models.TextField(blank=True)

    objects = CharacterManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("name"), "player", name="unique_character_player"
            )
        ]

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name, self.player_id)

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
    def initiative(self) -> int:
        return self.value_dexterity

    @property
    def attack_melee(self) -> int:
        return self.level + self.modifier_strength

    @property
    def attack_range(self) -> int:
        return self.level + self.modifier_dexterity

    @property
    def attack_magic(self) -> int:
        modifier_map = {
            Profile.MagicalStrength.INTELLIGENCE: self.modifier_intelligence,
            Profile.MagicalStrength.WISDOM: self.modifier_wisdom,
            Profile.MagicalStrength.CHARISMA: self.modifier_charisma,
        }

        return self.level + modifier_map.get(
            Profile.MagicalStrength(self.profile.magical_strength)
        )

    @property
    def defense(self) -> int:
        return (
            10 + self.armor + self.shield + self.modifier_dexterity + self.defense_misc
        )

    @property
    def mana_max(self) -> int:
        return 2 * self.level + self.modifier_intelligence

    @property
    def mana_remaining(self) -> int:
        return self.mana_max - self.mana_consumed
