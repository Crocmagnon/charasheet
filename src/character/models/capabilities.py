from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel

from common.models import UniquelyNamedModel


class Path(UniquelyNamedModel, TimeStampedModel, models.Model):
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


class Capability(UniquelyNamedModel, TimeStampedModel, models.Model):
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


class RacialCapability(UniquelyNamedModel, TimeStampedModel, models.Model):
    race = models.ForeignKey("character.Race", on_delete=models.CASCADE)
    description = models.TextField()

    class Meta:
        verbose_name_plural = "Racial capabilities"
