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
        verbose_name="profil",
    )
    race = models.ForeignKey(
        "character.Race",
        on_delete=models.CASCADE,
        related_name="paths",
        blank=True,
        null=True,
        verbose_name="race",
    )

    class Category(models.TextChoices):
        PROFILE = "profile", "Profil"
        RACE = "race", "Race"
        PRESTIGE = "prestige", "Prestige"
        CREATURE = "creature", "Créature"

    category = models.CharField(
        max_length=20, choices=Category.choices, verbose_name="catégorie"
    )
    notes = models.TextField(blank=True, verbose_name="notes")

    class Meta:
        verbose_name = "Voie"
        verbose_name_plural = "Voies"


class Capability(DocumentedModel, UniquelyNamedModel, TimeStampedModel, models.Model):
    path = models.ForeignKey(
        "character.Path", on_delete=models.CASCADE, verbose_name="voie"
    )
    rank = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="rang"
    )
    limited = models.BooleanField(
        blank=True, null=False, default=False, verbose_name="limitée"
    )
    spell = models.BooleanField(
        blank=True, null=False, default=False, verbose_name="sort"
    )
    description = models.TextField(verbose_name="description")

    class Meta:
        constraints = [models.UniqueConstraint("path", "rank", name="unique_path_rank")]
        verbose_name = "Capacité"
        verbose_name_plural = "Capacités"


class RacialCapabilityManager(models.Manager):
    def get_by_natural_key(self, name: str, race_id: int):
        return self.get(name=name, race_id=race_id)


class RacialCapability(DocumentedModel, TimeStampedModel, models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, verbose_name="nom")
    race = models.ForeignKey(
        "character.Race", on_delete=models.CASCADE, verbose_name="race"
    )
    description = models.TextField(verbose_name="description")

    objects = RacialCapabilityManager()

    class Meta:
        verbose_name = "Capacité raciale"
        verbose_name_plural = "Capacités raciales"
        constraints = [models.UniqueConstraint("name", "race", name="unique_name_race")]

    def __str__(self):
        return f"{self.name} ({self.race})"

    def natural_key(self):
        return (self.name, self.race_id)
