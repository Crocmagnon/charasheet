# Generated by Django 4.1.4 on 2022-12-09 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("character", "0037_character_private"),
    ]

    operations = [
        migrations.AddField(
            model_name="character",
            name="profile_picture",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="profile_pictures",
                verbose_name="image de profil",
            ),
        ),
    ]