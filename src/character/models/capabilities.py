from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel

from common.models import DocumentedModel, UniquelyNamedModel


class Path(DocumentedModel, UniquelyNamedModel, TimeStampedModel, models.Model):
    profile = models.ForeignKey(
        "character.Profile",
        on_delete=models.CASCADE,
        related_name="paths",
        blank=True,
        null=True,
    )
    race = models.ForeignKey(
        "character.Race",
        on_delete=models.CASCADE,
        related_name="paths",
        blank=True,
        null=True,
    )

    class Category(models.TextChoices):
        PROFILE = "profile", "Profile"
        RACE = "race", "Race"
        PRESTIGE = "prestige", "Prestige"
        CREATURE = "creature", "Creature"

    category = models.CharField(max_length=20, choices=Category.choices)
    notes = models.TextField(blank=True)


class Capability(DocumentedModel, UniquelyNamedModel, TimeStampedModel, models.Model):
    path = models.ForeignKey("character.Path", on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    limited = models.BooleanField(blank=True, null=False, default=False)
    spell = models.BooleanField(blank=True, null=False, default=False)
    description = models.TextField()

    class Meta:
        constraints = [models.UniqueConstraint("path", "rank", name="unique_path_rank")]
        verbose_name_plural = "Capabilities"


class RacialCapabilityManager(models.Manager):
    def get_by_natural_key(self, name: str, race_id: int):
        return self.get(name=name, race_id=race_id)


class RacialCapability(DocumentedModel, TimeStampedModel, models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    race = models.ForeignKey("character.Race", on_delete=models.CASCADE)
    description = models.TextField()

    objects = RacialCapabilityManager()

    class Meta:
        verbose_name_plural = "Racial capabilities"
        constraints = [models.UniqueConstraint("name", "race", name="unique_name_race")]

    def __str__(self):
        return f"{self.name} ({self.race})"

    def natural_key(self):
        return (self.name, self.race_id)
