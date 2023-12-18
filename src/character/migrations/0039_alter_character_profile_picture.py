# Generated by Django 4.1.4 on 2022-12-28 07:56

import functools

from django.db import migrations, models

import character.models.character


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0038_character_profile_picture"),
    ]

    operations = [
        migrations.AlterField(
            model_name="character",
            name="profile_picture",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="profile_pictures",
                validators=[
                    functools.partial(
                        character.models.character.validate_image,
                        *(),
                        megabytes_limit=2,
                    ),
                ],
                verbose_name="image de profil",
            ),
        ),
    ]
