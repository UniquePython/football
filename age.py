from dataclasses import dataclass


@dataclass
class AgeRange:
    min: int
    max: int

    def __post_init__(self):
        self.min = self.min if self.min >= 16 else 16
        self.max = self.max if self.max <= 40 else 40


AgeInput = int | AgeRange
