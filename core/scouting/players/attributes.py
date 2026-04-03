"""Typed FM player attribute definitions shared by scouting and memory readers."""

from enum import StrEnum


class GoalkeepingAttribute(StrEnum):
    AERIAL_REACH = "Aerial Reach"
    COMMAND_OF_AREA = "Command Of Area"
    COMMUNICATION = "Communication"
    ECCENTRICITY = "Eccentricity"
    HANDLING = "Handling"
    KICKING = "Kicking"
    ONE_ON_ONES = "One On Ones"
    PUNCHING_TENDENCY = "Punching (Tendency)"
    REFLEXES = "Reflexes"
    RUSHING_OUT_TENDENCY = "Rushing Out (Tendency)"
    THROWING = "Throwing"


class TechnicalAttribute(StrEnum):
    CORNERS = "Corners"
    CROSSING = "Crossing"
    DRIBBLING = "Dribbling"
    FINISHING = "Finishing"
    FIRST_TOUCH = "First Touch"
    FREE_KICK_TAKING = "Free Kick Taking"
    HEADING = "Heading"
    LONG_SHOTS = "Long Shots"
    LONG_THROWS = "Long Throws"
    MARKING = "Marking"
    PASSING = "Passing"
    PENALTY_TAKING = "Penalty Taking"
    TACKLING = "Tackling"
    TECHNIQUE = "Technique"


class MentalAttribute(StrEnum):
    AGGRESSION = "Aggression"
    ANTICIPATION = "Anticipation"
    BRAVERY = "Bravery"
    COMPOSURE = "Composure"
    CONCENTRATION = "Concentration"
    DECISIONS = "Decisions"
    DETERMINATION = "Determination"
    FLAIR = "Flair"
    LEADERSHIP = "Leadership"
    OFF_THE_BALL = "Off The Ball"
    POSITIONING = "Positioning"
    TEAMWORK = "Teamwork"
    VISION = "Vision"
    WORK_RATE = "Work Rate"


class PhysicalAttribute(StrEnum):
    ACCELERATION = "Acceleration"
    AGILITY = "Agility"
    BALANCE = "Balance"
    JUMPING_REACH = "Jumping Reach"
    NATURAL_FITNESS = "Natural Fitness"
    PACE = "Pace"
    STAMINA = "Stamina"
    STRENGTH = "Strength"


class HiddenAttribute(StrEnum):
    CONSISTENCY = "Consistency"
    DIRTINESS = "Dirtiness"
    IMPORTANT_MATCHES = "Important Matches"
    INJURY_PRONENESS = "Injury Proneness"
    VERSATILITY = "Versatility"


class FootAttribute(StrEnum):
    LEFT_FOOT = "Left Foot"
    RIGHT_FOOT = "Right Foot"


class ATTRIBUTE:
    GOALKEEPING = GoalkeepingAttribute
    TECHNICAL = TechnicalAttribute
    MENTAL = MentalAttribute
    PHYSICAL = PhysicalAttribute
    HIDDEN = HiddenAttribute
    FOOT = FootAttribute


Attribute = GoalkeepingAttribute | TechnicalAttribute | MentalAttribute | PhysicalAttribute | HiddenAttribute | FootAttribute

# This is the order that player attributes are stored in memory
SCAN_ATTRIBUTES = (
    TechnicalAttribute.CROSSING,
    TechnicalAttribute.DRIBBLING,
    TechnicalAttribute.FINISHING,
    TechnicalAttribute.HEADING,
    TechnicalAttribute.LONG_SHOTS,
    TechnicalAttribute.MARKING,
    MentalAttribute.OFF_THE_BALL,
    TechnicalAttribute.PASSING,
    TechnicalAttribute.PENALTY_TAKING,
    TechnicalAttribute.TACKLING,
    MentalAttribute.VISION,
    GoalkeepingAttribute.HANDLING,
    GoalkeepingAttribute.AERIAL_REACH,
    GoalkeepingAttribute.COMMAND_OF_AREA,
    GoalkeepingAttribute.COMMUNICATION,
    GoalkeepingAttribute.KICKING,
    GoalkeepingAttribute.THROWING,
    MentalAttribute.ANTICIPATION,
    MentalAttribute.DECISIONS,
    GoalkeepingAttribute.ONE_ON_ONES,
    MentalAttribute.POSITIONING,
    GoalkeepingAttribute.REFLEXES,
    TechnicalAttribute.FIRST_TOUCH,
    TechnicalAttribute.TECHNIQUE,
    FootAttribute.LEFT_FOOT,
    FootAttribute.RIGHT_FOOT,
    MentalAttribute.FLAIR,
    TechnicalAttribute.CORNERS,
    MentalAttribute.TEAMWORK,
    MentalAttribute.WORK_RATE,
    TechnicalAttribute.LONG_THROWS,
    GoalkeepingAttribute.ECCENTRICITY,
    GoalkeepingAttribute.RUSHING_OUT_TENDENCY,
    GoalkeepingAttribute.PUNCHING_TENDENCY,
    PhysicalAttribute.ACCELERATION,
    TechnicalAttribute.FREE_KICK_TAKING,
    PhysicalAttribute.STRENGTH,
    PhysicalAttribute.STAMINA,
    PhysicalAttribute.PACE,
    PhysicalAttribute.JUMPING_REACH,
    MentalAttribute.LEADERSHIP,
    HiddenAttribute.DIRTINESS,
    PhysicalAttribute.BALANCE,
    MentalAttribute.BRAVERY,
    HiddenAttribute.CONSISTENCY,
    MentalAttribute.AGGRESSION,
    PhysicalAttribute.AGILITY,
    HiddenAttribute.IMPORTANT_MATCHES,
    HiddenAttribute.INJURY_PRONENESS,
    HiddenAttribute.VERSATILITY,
    PhysicalAttribute.NATURAL_FITNESS,
    MentalAttribute.DETERMINATION,
    MentalAttribute.COMPOSURE,
    MentalAttribute.CONCENTRATION,
)
