def clamp(value: float, low: float, high: float) -> float:
    """
    Clamp a value between a minimum and maximum.

    Args:
        value: The input value
        low: Minimum allowed value (inclusive)
        high: Maximum allowed value (inclusive)

    Returns:
        value if within range, otherwise low or high

    Example:
        >>> clamp(5.0, 0.0, 10.0)
        5.0
        >>> clamp(-3.0, 0.0, 10.0)
        0.0
        >>> clamp(15.0, 0.0, 10.0)
        10.0
    """
    return max(low, min(value, high))


def percent_change(old: float, new: float) -> float:
    """
    Calculate the percentage change from old to new.

    Formula: ((new - old) / old) * 100

    Args:
        old: Original value (must not be zero)
        new: New value

    Returns:
        Percentage change as a float

    Raises:
        ValueError: If old is zero (division by zero)

    Example:
        >>> percent_change(100.0, 110.0)
        10.0
        >>> percent_change(200.0, 150.0)
        -25.0
    """
    if old == 0:
        raise ValueError("Cannot compute percent change from zero")
    return ((new - old) / old) * 100


def normalize(values: list[float]) -> list[float]:
    """
    Normalize a list of values to the range [0, 1].

    Formula: (x - min) / (max - min)

    Args:
        values: List of numeric values

    Returns:
        Normalized values in [0, 1]. Returns the original list unchanged
        if all values are identical (range is zero).

    Example:
        >>> normalize([0.0, 50.0, 100.0])
        [0.0, 0.5, 1.0]
        >>> normalize([5.0, 5.0, 5.0])
        [5.0, 5.0, 5.0]
    """
    if not values:
        return []

    lo = min(values)
    hi = max(values)

    if hi == lo:
        return list(values)

    return [(v - lo) / (hi - lo) for v in values]
