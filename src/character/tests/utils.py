from functools import partial

from hypothesis.strategies import integers

VALUE_TO_MODIFIER = {
    1: -4,
    2: -4,
    3: -4,
    4: -3,
    5: -3,
    6: -2,
    7: -2,
    8: -1,
    9: -1,
    10: 0,
    11: 0,
    12: 1,
    13: 1,
    14: 2,
    15: 2,
    16: 3,
    17: 3,
    18: 4,
    19: 4,
    20: 5,
    21: 5,
}


def modifier_test(value: int) -> int:
    return VALUE_TO_MODIFIER[value]


ability_values = partial(integers, min_value=1, max_value=21)
levels = partial(integers, min_value=1)
