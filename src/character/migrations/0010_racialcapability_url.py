# Generated by Django 4.1.2 on 2022-10-30 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("character", "0009_remove_racialcapability_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="racialcapability",
            name="url",
            field=models.URLField(blank=True),
        ),
    ]