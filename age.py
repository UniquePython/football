from dataclasses import dataclass


@dataclass
class AgeRange:
    min: int
    max: int

    def __post_init__(self):
        if self.min > self.max:
            raise ValueError(f"min ({self.min}) cannot exceed max ({self.max})")

        self.min = self.min if self.min >= 16 else 16
        self.max = self.max if self.max <= 40 else 40


AgeInput = int | AgeRange
