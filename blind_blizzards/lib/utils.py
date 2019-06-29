from data.typing import Number


def value_map(
    unmapped: Number,
    min_start: Number,
    max_start: Number,
    min_end: Number,
    max_end: Number,
) -> float:
    """Takes a number between `min_start` and `max_start` (not enforced)
    and places it at an equivalent place between `min_end` and `max_end`
    e.g. `value_map(1, 0, 2, 4, 8)` -> 6.0"""
    # start by normalising the range
    value = unmapped - min_start
    original_width = max_start - min_start

    # now find the width of the target range
    target_width = max_end - min_end

    # multiply by target width and then divide by original width
    # this order preserves more precision without using a decimal.Decimal
    value *= target_width
    value /= original_width

    # finally, put it back in the desired range by adding the minimum
    value += min_end

    # return the mapped value
    return value
