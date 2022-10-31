# Generated by Django 4.1.2 on 2022-10-30 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("character", "0019_weapon_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="weapon",
            name="category",
            field=models.CharField(
                choices=[
                    ("MEL", "corps à corps"),
                    ("RAN", "à distance"),
                    ("NON", "aucune"),
                ],
                default="NON",
                max_length=3,
            ),
        ),
    ]