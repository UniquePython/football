import math
import random
from dataclasses import dataclass

from position import Position, Role


@dataclass
class RoleWeights:
    # Pace
    sprintSpeed: float
    # Shooting
    finishing: float
    shotPower: float
    longShots: float
    volleys: float
    # Passing
    vision: float
    crossing: float
    shortPassing: float
    longPassing: float
    # Dribbling
    agility: float
    ballControl: float
    dribbling: float
    composure: float
    # Defending
    interceptions: float
    standingTackle: float
    slidingTackle: float
    heading: float
    # Physical
    stamina: float
    strength: float
    aggression: float
    jumping: float
    # Keeping
    keepingDiving: float
    keepingHandling: float
    keepingReflexes: float
    keepingPositioning: float


ROLE_WEIGHTS: dict[Role, RoleWeights] = {
    Role.Attacker: RoleWeights(
        sprintSpeed=0.8,
        finishing=0.95,
        shotPower=0.8,
        longShots=0.6,
        volleys=0.5,
        vision=0.6,
        crossing=0.5,
        shortPassing=0.6,
        longPassing=0.4,
        agility=0.8,
        ballControl=0.85,
        dribbling=0.85,
        composure=0.8,
        interceptions=0.15,
        standingTackle=0.1,
        slidingTackle=0.05,
        heading=0.5,
        stamina=0.7,
        strength=0.65,
        aggression=0.5,
        jumping=0.6,
        keepingDiving=0.02,
        keepingHandling=0.02,
        keepingReflexes=0.02,
        keepingPositioning=0.02,
    ),
    Role.Midfielder: RoleWeights(
        sprintSpeed=0.6,
        finishing=0.5,
        shotPower=0.6,
        longShots=0.7,
        volleys=0.4,
        vision=0.9,
        crossing=0.6,
        shortPassing=0.9,
        longPassing=0.8,
        agility=0.7,
        ballControl=0.8,
        dribbling=0.7,
        composure=0.75,
        interceptions=0.75,
        standingTackle=0.6,
        slidingTackle=0.5,
        heading=0.4,
        stamina=0.9,
        strength=0.6,
        aggression=0.6,
        jumping=0.4,
        keepingDiving=0.03,
        keepingHandling=0.03,
        keepingReflexes=0.03,
        keepingPositioning=0.03,
    ),
    Role.Defender: RoleWeights(
        sprintSpeed=0.75,
        finishing=0.1,
        shotPower=0.2,
        longShots=0.2,
        volleys=0.05,
        vision=0.5,
        crossing=0.3,
        shortPassing=0.7,
        longPassing=0.6,
        agility=0.5,
        ballControl=0.6,
        dribbling=0.3,
        composure=0.7,
        interceptions=0.9,
        standingTackle=0.9,
        slidingTackle=0.8,
        heading=0.85,
        stamina=0.7,
        strength=0.85,
        aggression=0.8,
        jumping=0.8,
        keepingDiving=0.05,
        keepingHandling=0.05,
        keepingReflexes=0.05,
        keepingPositioning=0.05,
    ),
    Role.Keeper: RoleWeights(
        sprintSpeed=0.3,
        finishing=0.05,
        shotPower=0.1,
        longShots=0.03,
        volleys=0.02,
        vision=0.4,
        crossing=0.1,
        shortPassing=0.6,
        longPassing=0.5,
        agility=0.6,
        ballControl=0.4,
        dribbling=0.1,
        composure=0.8,
        interceptions=0.3,
        standingTackle=0.1,
        slidingTackle=0.05,
        heading=0.4,
        stamina=0.5,
        strength=0.6,
        aggression=0.4,
        jumping=0.85,
        keepingDiving=0.95,
        keepingHandling=0.9,
        keepingReflexes=0.95,
        keepingPositioning=0.9,
    ),
}


@dataclass
class AttributeValue:
    current: int
    potential: int


@dataclass
class PaceAttributes:
    sprintSpeed: AttributeValue


@dataclass
class ShootingAttributes:
    finishing: AttributeValue
    shotPower: AttributeValue
    longShots: AttributeValue
    volleys: AttributeValue


@dataclass
class PassingAttributes:
    vision: AttributeValue
    crossing: AttributeValue
    shortPassing: AttributeValue
    longPassing: AttributeValue


@dataclass
class DribblingAttributes:
    agility: AttributeValue
    ballControl: AttributeValue
    dribbling: AttributeValue
    composure: AttributeValue


@dataclass
class DefendingAttributes:
    interceptions: AttributeValue
    standingTackle: AttributeValue
    slidingTackle: AttributeValue
    heading: AttributeValue


@dataclass
class PhysicalAttributes:
    stamina: AttributeValue
    strength: AttributeValue
    aggression: AttributeValue
    jumping: AttributeValue


@dataclass
class KeepingAttributes:
    diving: AttributeValue
    handling: AttributeValue
    reflexes: AttributeValue
    positioning: AttributeValue


QUALITY_FLOOR = 40
QUALITY_CEILING = 99


@dataclass
class AgeProfile:
    peakAge: int
    spread: float


AGE_PROFILES = {
    "physical": AgeProfile(peakAge=24, spread=4),
    "technical": AgeProfile(peakAge=28, spread=5),
    "mental": AgeProfile(peakAge=30, spread=6),
    "keeping": AgeProfile(peakAge=30, spread=5),
}


def _agePeakModifier(age: int, profile: AgeProfile) -> float:
    return math.exp(-0.5 * ((age - profile.peakAge) / profile.spread) ** 2)


def _generateValue(age: int, weight: float, profile: AgeProfile) -> int:
    modifier = _agePeakModifier(age, profile)
    mean = QUALITY_FLOOR + (QUALITY_CEILING - QUALITY_FLOOR) * weight * modifier
    raw = random.normalvariate(mean, 5)
    return max(1, min(100, int(raw)))


def _generatePotential(current: int, age: int) -> int:
    maxGap = 25
    meanGap = maxGap * max(0, (1 - age / 40))
    gap = max(0, int(random.normalvariate(meanGap, 3)))
    return max(1, min(100, current + gap))


def _av(age: int, weight: float, profile: AgeProfile) -> AttributeValue:
    current = _generateValue(age, weight, profile)
    potential = _generatePotential(current, age)
    return AttributeValue(current=current, potential=potential)


@dataclass
class Attributes:
    pace: PaceAttributes
    shooting: ShootingAttributes
    passing: PassingAttributes
    dribbling: DribblingAttributes
    defending: DefendingAttributes
    physical: PhysicalAttributes
    keeping: KeepingAttributes

    @classmethod
    def generate(cls, position: Position, age: int) -> "Attributes":
        w = ROLE_WEIGHTS[position.role]
        p = AGE_PROFILES

        return cls(
            pace=PaceAttributes(
                sprintSpeed=_av(age, w.sprintSpeed, p["physical"]),
            ),
            shooting=ShootingAttributes(
                finishing=_av(age, w.finishing, p["technical"]),
                shotPower=_av(age, w.shotPower, p["physical"]),
                longShots=_av(age, w.longShots, p["technical"]),
                volleys=_av(age, w.volleys, p["technical"]),
            ),
            passing=PassingAttributes(
                vision=_av(age, w.vision, p["mental"]),
                crossing=_av(age, w.crossing, p["technical"]),
                shortPassing=_av(age, w.shortPassing, p["technical"]),
                longPassing=_av(age, w.longPassing, p["technical"]),
            ),
            dribbling=DribblingAttributes(
                agility=_av(age, w.agility, p["physical"]),
                ballControl=_av(age, w.ballControl, p["technical"]),
                dribbling=_av(age, w.dribbling, p["technical"]),
                composure=_av(age, w.composure, p["mental"]),
            ),
            defending=DefendingAttributes(
                interceptions=_av(age, w.interceptions, p["mental"]),
                standingTackle=_av(age, w.standingTackle, p["technical"]),
                slidingTackle=_av(age, w.slidingTackle, p["technical"]),
                heading=_av(age, w.heading, p["physical"]),
            ),
            physical=PhysicalAttributes(
                stamina=_av(age, w.stamina, p["physical"]),
                strength=_av(age, w.strength, p["physical"]),
                aggression=_av(age, w.aggression, p["mental"]),
                jumping=_av(age, w.jumping, p["physical"]),
            ),
            keeping=KeepingAttributes(
                diving=_av(age, w.keepingDiving, p["keeping"]),
                handling=_av(age, w.keepingHandling, p["keeping"]),
                reflexes=_av(age, w.keepingReflexes, p["keeping"]),
                positioning=_av(age, w.keepingPositioning, p["keeping"]),
            ),
        )

    def _weightedSum(self, role: "Role", use_potential: bool = False) -> float:
        w = ROLE_WEIGHTS[role]

        def v(attr: AttributeValue) -> int:
            return attr.potential if use_potential else attr.current

        return (
            # Pace
            v(self.pace.sprintSpeed) * w.sprintSpeed
            +
            # Shooting
            v(self.shooting.finishing) * w.finishing
            + v(self.shooting.shotPower) * w.shotPower
            + v(self.shooting.longShots) * w.longShots
            + v(self.shooting.volleys) * w.volleys
            +
            # Passing
            v(self.passing.vision) * w.vision
            + v(self.passing.crossing) * w.crossing
            + v(self.passing.shortPassing) * w.shortPassing
            + v(self.passing.longPassing) * w.longPassing
            +
            # Dribbling
            v(self.dribbling.agility) * w.agility
            + v(self.dribbling.ballControl) * w.ballControl
            + v(self.dribbling.dribbling) * w.dribbling
            + v(self.dribbling.composure) * w.composure
            +
            # Defending
            v(self.defending.interceptions) * w.interceptions
            + v(self.defending.standingTackle) * w.standingTackle
            + v(self.defending.slidingTackle) * w.slidingTackle
            + v(self.defending.heading) * w.heading
            +
            # Physical
            v(self.physical.stamina) * w.stamina
            + v(self.physical.strength) * w.strength
            + v(self.physical.aggression) * w.aggression
            + v(self.physical.jumping) * w.jumping
            +
            # Keeping
            v(self.keeping.diving) * w.keepingDiving
            + v(self.keeping.handling) * w.keepingHandling
            + v(self.keeping.reflexes) * w.keepingReflexes
            + v(self.keeping.positioning) * w.keepingPositioning
        )

    def _weightSum(self, role: "Role") -> float:
        w = ROLE_WEIGHTS[role]
        return (
            w.sprintSpeed
            + w.finishing
            + w.shotPower
            + w.longShots
            + w.volleys
            + w.vision
            + w.crossing
            + w.shortPassing
            + w.longPassing
            + w.agility
            + w.ballControl
            + w.dribbling
            + w.composure
            + w.interceptions
            + w.standingTackle
            + w.slidingTackle
            + w.heading
            + w.stamina
            + w.strength
            + w.aggression
            + w.jumping
            + w.keepingDiving
            + w.keepingHandling
            + w.keepingReflexes
            + w.keepingPositioning
        )

    def overall(self, role: "Role") -> int:
        return round(
            self._weightedSum(role, use_potential=False) / self._weightSum(role)
        )

    def potential(self, role: "Role") -> int:
        return round(
            self._weightedSum(role, use_potential=True) / self._weightSum(role)
        )
