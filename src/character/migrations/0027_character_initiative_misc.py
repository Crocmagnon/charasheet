# Generated by Django 4.1.2 on 2022-11-02 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("character", "0026_alter_capability_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="character",
            name="initiative_misc",
            field=models.SmallIntegerField(default=0, verbose_name="divers initiative"),
        ),
    ]