# Generated by Django 4.1.2 on 2022-10-29 09:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0006_alter_path_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="capability",
            name="limited",
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name="capability",
            name="spell",
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
