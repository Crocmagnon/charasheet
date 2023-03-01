from django.db import models


class Pet(models.Model):
    # Fields are: name, health_max, health_remaining, modifier_strength,
    # modifier_dexterity, modifier_constitution, modifier_intelligence,
    # modifier_wisdom, modifier_charisma, damage, initiative, defense, attack,
    # recovery and notes.
    name = models.CharField(max_length=100, verbose_name="nom")
    owner = models.ForeignKey(
        "character.Character",
        on_delete=models.CASCADE,
        related_name="pets",
    )
    health_max = models.PositiveIntegerField(verbose_name="points de vie maximum")
    health_remaining = models.PositiveIntegerField(
        verbose_name="points de vie restants",
    )
    modifier_strength = models.IntegerField(verbose_name="modificateur force")
    modifier_dexterity = models.IntegerField(verbose_name="modificateur dextérité")
    modifier_constitution = models.IntegerField(
        verbose_name="modificateur constitution",
    )
    modifier_intelligence = models.IntegerField(
        verbose_name="modificateur intelligence",
    )
    modifier_wisdom = models.IntegerField(verbose_name="modificateur sagesse")
    modifier_charisma = models.IntegerField(verbose_name="modificateur charisme")
    damage = models.PositiveIntegerField(verbose_name="dégâts")
    initiative = models.PositiveIntegerField(verbose_name="initiative")
    defense = models.PositiveIntegerField(verbose_name="défense")
    attack = models.PositiveIntegerField(verbose_name="attaque")
    recovery = models.CharField(max_length=100, verbose_name="récupération", blank=True)
    notes = models.TextField(verbose_name="notes", blank=True)

    def __str__(self):
        return self.name

    @property
    def health_remaining_percent(self) -> float:
        if self.health_max == 0:
            return 0
        return self.health_remaining / self.health_max * 100
