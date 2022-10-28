from django.db import models
from django_extensions.db.models import TimeStampedModel

from common.models import UniquelyNamedModel


class Weapon(UniquelyNamedModel, TimeStampedModel, models.Model):
    damage = models.CharField(max_length=50, blank=True)
    special = models.TextField(blank=True)
