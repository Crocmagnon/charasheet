# Generated by Django 4.1.2 on 2022-11-01 08:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0025_alter_capability_path"),
    ]

    operations = [
        migrations.AlterField(
            model_name="capability",
            name="name",
            field=models.CharField(max_length=100, verbose_name="nom"),
        ),
    ]
