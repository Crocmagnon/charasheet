# Generated by Django 4.1.2 on 2022-10-30 23:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "character",
            "0023_alter_character_armor_alter_character_defense_misc_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="character",
            name="notes",
            field=models.TextField(
                blank=True,
                default="#### Traits personnalisés\n\n#### Objectifs\n\n#### Langages\n\n#### Historique\n\n#### Handicaps\n\n#### Alignement\n\n#### Relations\n\n#### Religion\n",
                verbose_name="notes",
            ),
        ),
    ]
