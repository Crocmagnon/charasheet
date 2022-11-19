from django.db import models
from django.db.models import Q
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel

from character.models import Character
from common.models import UniquelyNamedModel, UniquelyNamedModelManager


class PartyQuerySet(models.QuerySet):
    def managed_by(self, user):
        return self.filter(game_master=user)

    def played_by(self, user):
        return self.filter(characters__in=Character.objects.filter(player=user))

    def related_to(self, user):
        return self.filter(
            Q(game_master=user)
            | Q(characters__in=Character.objects.filter(player=user))
            | Q(invited_characters__in=Character.objects.filter(player=user))
        ).distinct()

    def invited_to(self, user):
        return self.filter(invited_characters__in=Character.objects.filter(player=user))


class PartyManager(UniquelyNamedModelManager):
    pass


class Party(UniquelyNamedModel, TimeStampedModel, models.Model):
    game_master = models.ForeignKey(
        "common.User",
        on_delete=models.PROTECT,
        related_name="parties",
        verbose_name="meneur de jeu",
    )
    invited_characters = models.ManyToManyField(
        "character.Character",
        blank=True,
        related_name="invites",
        verbose_name="personnages invités",
    )
    characters = models.ManyToManyField(
        "character.Character",
        blank=True,
        related_name="parties",
        verbose_name="personnages",
    )

    objects = PartyManager.from_queryset(PartyQuerySet)()

    class Meta(UniquelyNamedModel.Meta, TimeStampedModel.Meta):
        verbose_name = "Groupe"
        verbose_name_plural = "Groupes"

    def get_absolute_url(self) -> str:
        return reverse("party:details", kwargs={"pk": self.pk})

    def reset_stats(self):
        for character in self.characters.all():
            character.reset_stats()
