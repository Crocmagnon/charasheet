from django.db import models
from django_extensions.db.models import TimeStampedModel

from common.models import DocumentedModel, UniquelyNamedModel


class Weapon(UniquelyNamedModel, DocumentedModel, TimeStampedModel, models.Model):
    class Category(models.TextChoices):
        MELEE = "MEL", "corps à corps"
        RANGE = "RAN", "à distance"
        NONE = "NON", "aucune"

    damage = models.CharField(max_length=50, blank=True, verbose_name="dégâts")
    special = models.TextField(blank=True, verbose_name="spécial")
    category = models.CharField(
        max_length=3, choices=Category.choices, default=Category.NONE
    )

    class Meta:
        verbose_name = "Arme"
        verbose_name_plural = "Armes"
