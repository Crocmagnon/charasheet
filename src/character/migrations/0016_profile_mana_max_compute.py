# Generated by Django 4.1.2 on 2022-10-30 21:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0015_character_recovery_points_remaining"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="mana_max_compute",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "Pas de mana"),
                    (1, "1 x niveau + mod. magique"),
                    (2, "2 x niveau + mod. magique"),
                ],
                default=0,
                verbose_name="calcul mana max",
            ),
        ),
    ]
