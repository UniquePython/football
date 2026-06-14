def clamp(lower: int, upper: int, value: int) -> int:
    return max(lower, min(value, upper))
