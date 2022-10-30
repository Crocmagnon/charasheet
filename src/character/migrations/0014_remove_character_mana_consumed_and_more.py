# Generated by Django 4.1.2 on 2022-10-30 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("character", "0013_character_money_pa_character_money_pc_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="character",
            name="mana_consumed",
        ),
        migrations.AddField(
            model_name="character",
            name="mana_remaining",
            field=models.PositiveSmallIntegerField(
                default=0, verbose_name="mana restant"
            ),
        ),
    ]