# Generated by Django 4.1.2 on 2022-10-29 08:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0004_remove_character_mana_max_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="notes",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="character",
            name="mana_consumed",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="profile",
            name="magical_strength",
            field=models.CharField(
                choices=[
                    ("NON", "None"),
                    ("INT", "Intelligence"),
                    ("SAG", "Wisdom"),
                    ("CHA", "Charisma"),
                ],
                default="NON",
                max_length=3,
            ),
        ),
    ]
