# Generated by Django 4.1.2 on 2022-10-30 21:43

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0016_profile_mana_max_compute"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="character",
            name="luck_points_max",
        ),
    ]
