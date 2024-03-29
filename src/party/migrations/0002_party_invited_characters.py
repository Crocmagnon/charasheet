# Generated by Django 4.1.2 on 2022-11-06 14:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0036_delete_party"),
        ("party", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="party",
            name="invited_characters",
            field=models.ManyToManyField(
                blank=True,
                related_name="invites",
                to="character.character",
                verbose_name="personnages invités",
            ),
        ),
    ]
