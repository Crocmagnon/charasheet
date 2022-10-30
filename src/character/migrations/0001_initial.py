# Generated by Django 4.1.2 on 2022-10-28 21:52

import django.core.validators
import django.db.models.deletion
import django.db.models.functions.text
import django_extensions.db.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Capability",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                (
                    "rank",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ]
                    ),
                ),
                ("limited", models.BooleanField(blank=True)),
                ("spell", models.BooleanField(blank=True)),
                ("description", models.TextField()),
            ],
            options={
                "verbose_name_plural": "Capabilities",
            },
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                (
                    "magical_strength",
                    models.CharField(
                        choices=[
                            ("NON", "None"),
                            ("INT", "Intelligence"),
                            ("WIS", "Wisdom"),
                            ("CHA", "Charisma"),
                        ],
                        default="NON",
                        max_length=3,
                    ),
                ),
                (
                    "life_dice",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (4, "D4"),
                            (6, "D6"),
                            (8, "D8"),
                            (10, "D10"),
                            (12, "D12"),
                            (20, "D20"),
                        ]
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Race",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Weapon",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                ("damage", models.CharField(blank=True, max_length=50)),
                ("special", models.TextField(blank=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="RacialCapability",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                ("description", models.TextField()),
                (
                    "race",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="character.race"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Racial capabilities",
            },
        ),
        migrations.CreateModel(
            name="Path",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("profile", "Profile"),
                            ("race", "Race"),
                            ("prestige", "Prestige"),
                        ],
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField()),
                (
                    "profile",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="paths",
                        to="character.profile",
                    ),
                ),
                (
                    "race",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="paths",
                        to="character.race",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Character",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("level", models.PositiveSmallIntegerField()),
                (
                    "gender",
                    models.CharField(
                        choices=[("M", "Male"), ("F", "Female"), ("O", "Other")],
                        default="O",
                        max_length=1,
                    ),
                ),
                ("age", models.PositiveSmallIntegerField()),
                ("height", models.PositiveSmallIntegerField()),
                ("weight", models.PositiveSmallIntegerField()),
                ("value_strength", models.PositiveSmallIntegerField()),
                ("value_dexterity", models.PositiveSmallIntegerField()),
                ("value_constitution", models.PositiveSmallIntegerField()),
                ("value_intelligence", models.PositiveSmallIntegerField()),
                ("value_wisdom", models.PositiveSmallIntegerField()),
                ("value_charisma", models.PositiveSmallIntegerField()),
                ("health_max", models.PositiveSmallIntegerField()),
                ("health_remaining", models.PositiveSmallIntegerField()),
                ("armor", models.PositiveSmallIntegerField()),
                ("shield", models.PositiveSmallIntegerField()),
                ("defense_misc", models.SmallIntegerField()),
                ("equipment", models.TextField()),
                ("luck_points_max", models.PositiveSmallIntegerField()),
                ("luck_points_remaining", models.PositiveSmallIntegerField()),
                ("mana_max", models.PositiveSmallIntegerField()),
                ("mana_remaining", models.PositiveSmallIntegerField()),
                ("notes", models.TextField()),
                ("capabilities", models.ManyToManyField(to="character.capability")),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="characters",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="characters",
                        to="character.profile",
                    ),
                ),
                (
                    "race",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="characters",
                        to="character.race",
                    ),
                ),
                (
                    "racial_capability",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="characters",
                        to="character.racialcapability",
                    ),
                ),
                ("weapons", models.ManyToManyField(to="character.weapon")),
            ],
        ),
        migrations.AddField(
            model_name="capability",
            name="path",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="character.path"
            ),
        ),
        migrations.AddConstraint(
            model_name="character",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("name"),
                models.F("player"),
                name="unique_character_player",
            ),
        ),
        migrations.AddConstraint(
            model_name="capability",
            constraint=models.UniqueConstraint(
                models.F("path"), models.F("rank"), name="unique_path_rank"
            ),
        ),
    ]