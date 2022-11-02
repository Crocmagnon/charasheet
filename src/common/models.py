from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class UniquelyNamedModelManager(models.Manager):
    def get_by_natural_key(self, name: str):
        return self.get(name=name)


class UniquelyNamedModel(models.Model):
    name = models.CharField(
        max_length=100, blank=False, null=False, unique=True, verbose_name="nom"
    )
    objects = UniquelyNamedModelManager()

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


class DocumentedModel(models.Model):
    url = models.URLField(blank=True, null=False, verbose_name="url")

    class Meta:
        abstract = True
