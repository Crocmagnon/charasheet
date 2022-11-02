from django.db import models
from django_extensions.db.models import TimeStampedModel

from common.models import UniquelyNamedModel


class Party(UniquelyNamedModel, TimeStampedModel, models.Model):
    game_master = models.ForeignKey(
        "common.User",
        on_delete=models.PROTECT,
        related_name="parties",
        verbose_name="meneur de jeu",
    )
    characters = models.ManyToManyField(
        "character.Character",
        blank=True,
        related_name="parties",
        verbose_name="personnages",
    )

    class Meta(UniquelyNamedModel.Meta, TimeStampedModel.Meta):
        verbose_name = "Groupe"
        verbose_name_plural = "Groupes"
