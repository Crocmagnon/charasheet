# Generated by Django 4.1.2 on 2022-10-30 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("character", "0012_alter_capability_options_alter_character_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="character",
            name="money_pa",
            field=models.PositiveSmallIntegerField(default=0, verbose_name="PA"),
        ),
        migrations.AddField(
            model_name="character",
            name="money_pc",
            field=models.PositiveSmallIntegerField(default=0, verbose_name="PC"),
        ),
        migrations.AddField(
            model_name="character",
            name="money_po",
            field=models.PositiveSmallIntegerField(default=0, verbose_name="PO"),
        ),
        migrations.AddField(
            model_name="character",
            name="money_pp",
            field=models.PositiveSmallIntegerField(default=0, verbose_name="PP"),
        ),
    ]
