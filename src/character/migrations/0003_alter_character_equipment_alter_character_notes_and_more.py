# Generated by Django 4.1.2 on 2022-10-28 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "character",
            "0002_alter_character_capabilities_alter_character_weapons_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="character",
            name="equipment",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="character",
            name="notes",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="path",
            name="notes",
            field=models.TextField(blank=True),
        ),
    ]
