import pytest
from hypothesis import given
from hypothesis.strategies import integers

from character.models.character import Character, Profile
from character.models.dice import Dice
from character.tests.utils import ability_values, levels, modifier_test


@pytest.mark.parametrize(
    "value,expected",
    [
        (1, -4),
        (2, -4),
        (3, -4),
        (4, -3),
        (5, -3),
        (6, -2),
        (7, -2),
        (8, -1),
        (9, -1),
        (10, 0),
        (11, 0),
        (12, 1),
        (13, 1),
        (14, 2),
        (15, 2),
        (16, 3),
        (17, 3),
        (18, 4),
        (19, 4),
        (20, 5),
        (21, 5),
    ],
)
@pytest.mark.parametrize(
    "ability",
    ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"],
)
def test_modifier_values(value, expected, ability):
    character = Character()
    value_attribute = f"value_{ability}"
    setattr(character, value_attribute, value)
    modifier_attribute = f"modifier_{ability}"
    assert getattr(character, modifier_attribute) == expected


@given(ability_values())
def test_initiative(dex):
    assert Character(value_dexterity=dex).initiative == dex


@given(level=levels(), strength=ability_values())
def test_attack_melee(level, strength):
    character = Character(level=level, value_strength=strength)
    assert character.attack_melee == level + modifier_test(strength)


@given(level=levels(), dexterity=ability_values())
def test_attack_range(level, dexterity):
    character = Character(level=level, value_dexterity=dexterity)
    assert character.attack_range == level + modifier_test(dexterity)


@given(armor=integers(), shield=integers(), dexterity=ability_values(), misc=integers())
def test_defense(armor, shield, dexterity, misc):
    char = Character(
        armor=armor, shield=shield, value_dexterity=dexterity, defense_misc=misc
    )
    assert char.defense == 10 + armor + shield + modifier_test(dexterity) + misc


@given(level=levels(), intelligence=ability_values())
def test_mana_max_mage(level, intelligence):
    profile = Profile(
        name="Magicien",
        life_dice=Dice.D4,
        magical_strength=Profile.MagicalStrength.INTELLIGENCE,
        mana_max_compute=Profile.ManaMax.DOUBLE_LEVEL,
    )
    char = Character(level=level, profile=profile, value_intelligence=intelligence)
    assert char.mana_max == 2 * level + modifier_test(intelligence)


@given(level=levels(), wisdom=ability_values())
def test_mana_max_druid(level, wisdom):
    profile = Profile(
        name="Druide",
        life_dice=Dice.D4,
        magical_strength=Profile.MagicalStrength.WISDOM,
        mana_max_compute=Profile.ManaMax.LEVEL,
    )
    char = Character(level=level, profile=profile, value_wisdom=wisdom)
    assert char.mana_max == level + modifier_test(wisdom)
