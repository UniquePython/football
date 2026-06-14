from position import Position


class Formation:
    def __init__(self, lines: list[list[Position]]):
        if not lines:
            raise ValueError("Formation must have at least one line")

        total = sum(len(line) for line in lines)
        if total != 10:
            raise ValueError(
                f"Formation must have exactly 10 outfield positions, got {total}"
            )

        for i, line in enumerate(lines):
            if not line:
                raise ValueError(f"Line {i + 1} is empty")

        self.lines = lines

    @property
    def name(self) -> str:
        return "-".join(str(len(line)) for line in self.lines)

    @property
    def positions(self) -> list[Position]:
        return [p for line in self.lines for p in line]

    @property
    def defensiveness(self) -> float:
        return sum(p.defensiveness for p in self.positions)

    @property
    def offensiveness(self) -> float:
        return sum(p.offensiveness for p in self.positions)

    def __str__(self) -> str:
        return self.name


# 3-4-3
F_3_4_3 = Formation(
    [
        [Position.LB, Position.CB, Position.RB],
        [Position.LM, Position.CM, Position.CM, Position.RM],
        [Position.LW, Position.ST, Position.RW],
    ]
)

# 3-5-2
F_3_5_2 = Formation(
    [
        [Position.LB, Position.CB, Position.RB],
        [Position.CDM, Position.LM, Position.CM, Position.RM, Position.CAM],
        [Position.ST, Position.ST],
    ]
)

# 3-4-2-1
F_3_4_2_1 = Formation(
    [
        [Position.LB, Position.CB, Position.RB],
        [Position.CDM, Position.CM, Position.CM, Position.CDM],
        [Position.CAM, Position.CAM],
        [Position.ST],
    ]
)

# 3-3-3-1
F_3_3_3_1 = Formation(
    [
        [Position.LB, Position.CB, Position.RB],
        [Position.CDM, Position.CM, Position.CDM],
        [Position.CAM, Position.CAM, Position.CAM],
        [Position.ST],
    ]
)

# 3-2-4-1
F_3_2_4_1 = Formation(
    [
        [Position.LB, Position.CB, Position.RB],
        [Position.CDM, Position.CDM],
        [Position.LW, Position.CAM, Position.CAM, Position.RW],
        [Position.ST],
    ]
)


# 4-3-3
F_4_3_3 = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.RB],
        [Position.CM, Position.CM, Position.CM],
        [Position.LW, Position.ST, Position.RW],
    ]
)

# 4-3-3 attacking
F_4_3_3_ATT = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.RB],
        [Position.CDM, Position.CM, Position.CAM],
        [Position.LW, Position.ST, Position.RW],
    ]
)

# 4-3-3 defensive
F_4_3_3_DEF = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.RB],
        [Position.CDM, Position.CDM, Position.CM],
        [Position.LW, Position.ST, Position.RW],
    ]
)

# 4-4-2
F_4_4_2 = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.RB],
        [Position.LM, Position.CM, Position.CM, Position.RM],
        [Position.ST, Position.ST],
    ]
)

# 4-4-2 defensive
F_4_4_2_DEF = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.RB],
        [Position.LM, Position.CDM, Position.CM, Position.RM],
        [Position.ST, Position.ST],
    ]
)

# 4-2-3-1
F_4_2_3_1 = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.RB],
        [Position.CDM, Position.CDM],
        [Position.LW, Position.CAM, Position.RW],
        [Position.ST],
    ]
)

# 4-1-2-3
F_4_1_2_3 = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.RB],
        [Position.CDM],
        [Position.CM, Position.CM],
        [Position.LW, Position.ST, Position.RW],
    ]
)

# 4-1-4-1
F_4_1_4_1 = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.RB],
        [Position.CDM],
        [Position.LM, Position.CM, Position.CM, Position.RM],
        [Position.ST],
    ]
)

# 4-2-2-2
F_4_2_2_2 = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.RB],
        [Position.CDM, Position.CDM],
        [Position.CAM, Position.CAM],
        [Position.ST, Position.ST],
    ]
)

# 4-5-1
F_4_5_1 = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.RB],
        [Position.CDM, Position.LM, Position.CM, Position.RM, Position.CAM],
        [Position.ST],
    ]
)

# 4-5-1 defensive
F_4_5_1_DEF = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.RB],
        [Position.CDM, Position.CDM, Position.LM, Position.CM, Position.RM],
        [Position.ST],
    ]
)

# 5-3-2
F_5_3_2 = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.CB, Position.RB],
        [Position.LM, Position.CM, Position.RM],
        [Position.ST, Position.ST],
    ]
)

# 5-3-2 defensive
F_5_3_2_DEF = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.CB, Position.RB],
        [Position.CDM, Position.CDM, Position.CM],
        [Position.ST, Position.ST],
    ]
)

# 5-4-1
F_5_4_1 = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.CB, Position.RB],
        [Position.CDM, Position.LM, Position.RM, Position.CAM],
        [Position.ST],
    ]
)

# 5-4-1 defensive
F_5_4_1_DEF = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.CB, Position.RB],
        [Position.CDM, Position.CDM, Position.CM, Position.CM],
        [Position.ST],
    ]
)

# 5-2-3
F_5_2_3 = Formation(
    [
        [Position.LB, Position.CB, Position.CB, Position.CB, Position.RB],
        [Position.CDM, Position.CM],
        [Position.LW, Position.ST, Position.RW],
    ]
)

ALL_FORMATIONS = [
    F_3_4_3,
    F_3_5_2,
    F_3_4_2_1,
    F_3_3_3_1,
    F_3_2_4_1,
    F_4_3_3,
    F_4_3_3_ATT,
    F_4_3_3_DEF,
    F_4_4_2,
    F_4_4_2_DEF,
    F_4_2_3_1,
    F_4_1_2_3,
    F_4_1_4_1,
    F_4_2_2_2,
    F_4_5_1,
    F_4_5_1_DEF,
    F_5_3_2,
    F_5_3_2_DEF,
    F_5_4_1,
    F_5_4_1_DEF,
    F_5_2_3,
]
