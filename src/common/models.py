from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Default custom user model for My Awesome Project."""

    pass


class UniquelyNamedModelManager(models.Manager):
    def get_by_natural_key(self, name: str):
        return self.get(name=name)


class UniquelyNamedModel(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    objects = UniquelyNamedModelManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @property
    def natural_key(self):
        return (self.name,)
