# Generated by Django 4.1.2 on 2022-10-31 21:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0024_alter_character_notes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="capability",
            name="path",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="capabilities",
                to="character.path",
                verbose_name="voie",
            ),
        ),
    ]
