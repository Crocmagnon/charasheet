# Generated by Django 4.1.2 on 2022-10-30 22:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0017_remove_character_luck_points_max"),
    ]

    operations = [
        migrations.AddField(
            model_name="character",
            name="damage_reduction",
            field=models.TextField(blank=True, verbose_name="réduction de dégâts"),
        ),
    ]
