import pytest

from character.models.character import modifier


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
def test_modifier_values(value, expected):
    assert modifier(value) == expected
