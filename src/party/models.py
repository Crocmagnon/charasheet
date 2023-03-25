from django.db import models
from django.db.models import F, Q
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel

from character.models import Character
from common.models import UniquelyNamedModel, UniquelyNamedModelManager


class PartyQuerySet(models.QuerySet):
    def managed_by(self, user):
        return self.filter(game_master=user)

    def played_by(self, user):
        return self.filter(characters__in=Character.objects.filter(player=user))

    def played_or_mastered_by(self, user):
        return self.filter(
            Q(game_master=user)
            | Q(characters__in=Character.objects.filter(player=user)),
        ).distinct()

    def related_to(self, user):
        return self.filter(
            Q(game_master=user)
            | Q(characters__in=Character.objects.filter(player=user))
            | Q(invited_characters__in=Character.objects.filter(player=user)),
        ).distinct()

    def invited_to(self, user):
        return self.filter(invited_characters__in=Character.objects.filter(player=user))


class PartyManager(UniquelyNamedModelManager):
    pass


class Party(UniquelyNamedModel, TimeStampedModel, models.Model):  # noqa: DJ008
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


class BattleEffectQuerySet(models.QuerySet):
    def increase_rounds(self):
        self.temporary().update(remaining_rounds=F("remaining_rounds") + 1)

    def decrease_rounds(self):
        self.active().update(remaining_rounds=F("remaining_rounds") - 1)

    def active(self):
        return self.filter(remaining_rounds__gt=0)

    def terminated(self):
        return self.filter(remaining_rounds=0)

    def permanent(self):
        return self.filter(remaining_rounds=-1)

    def temporary(self):
        return self.exclude(remaining_rounds=-1)


class BattleEffectManager(models.Manager):
    pass


class BattleEffect(TimeStampedModel, models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, verbose_name="nom")
    target = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        verbose_name="cible",
    )
    description = models.TextField(blank=True, null=False, verbose_name="description")
    remaining_rounds = models.SmallIntegerField(
        blank=False,
        default=-1,
        verbose_name="nombre de tours restants",
        help_text="-1 pour un effet permanent",
    )
    party = models.ForeignKey(
        "party.Party",
        on_delete=models.CASCADE,
        related_name="effects",
        verbose_name="groupe",
    )
    created_by = models.ForeignKey(
        "common.User",
        on_delete=models.CASCADE,
        related_name="effects",
        verbose_name="créé par",
    )

    objects = BattleEffectManager.from_queryset(BattleEffectQuerySet)()

    def __str__(self):
        return self.name

    @property
    def remaining_percent(self) -> float:
        max_display_percent = 5
        if self.remaining_rounds >= max_display_percent or self.remaining_rounds < 0:
            return 100
        return self.remaining_rounds / max_display_percent * 100
