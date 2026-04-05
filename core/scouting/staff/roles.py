"""Staff/coaching domain definitions shared across staff tools."""

from enum import IntEnum, StrEnum


class StaffMetric(StrEnum):
    DISCIPLINE = "dis"
    DETERMINATION = "det"
    GOALKEEPING_SHOT_STOPPING = "gks"
    MOTIVATING = "mot"
    TACTICAL_KNOWLEDGE = "tkn"
    ATTACKING = "att"
    DEFENDING = "def"
    FITNESS = "fit"
    MENTAL = "men"
    TECHNICAL = "tec"
    TACTICAL = "tac"
    GOALKEEPING_DISTRIBUTION = "gkd"
    GOALKEEPING_HANDLING = "gkh"
    SET_PIECES = "set"
    DDM = "ddm"


class StaffArea(StrEnum):
    GOALKEEPING_SHOT_STOPPING = "GKS"
    GOALKEEPING_HANDLING = "GKH"
    DEFENDING_TACTICAL = "DTAC"
    DEFENDING_TECHNICAL = "DTEC"
    ATTACKING_TACTICAL = "ATAC"
    ATTACKING_TECHNICAL = "ATEC"
    POSSESSION_TACTICAL = "PTAC"
    POSSESSION_TECHNICAL = "PTEC"
    FITNESS_STRENGTH = "FITS"
    FITNESS_QUICKNESS = "FITQ"
    SET_PIECES = "SETP"

    @property
    def short_label(self):
        return self.value


TRAINING_AREAS = StaffArea


class Qualification(IntEnum):
    CONTINENTAL_PRO = 1
    CONTINENTAL_A = 2
    CONTINENTAL_B = 3
    CONTINENTAL_C = 4
    NATIONAL_A = 5
    NATIONAL_B = 6
    NATIONAL_C = 7

    @property
    def label(self):
        return self.name.replace("_", " ").title()


# The scaled coaching block used by both ordinary staff samples and the human
# manager lines up with visible Technical at 0x3E, visible Tactical at 0x3F,
# and Tactical Knowledge at 0x39.
STAFF_ATTRIBUTE_OFFSETS = {
    StaffMetric.DISCIPLINE: 0x1C,
    StaffMetric.DETERMINATION: 0x25,
    StaffMetric.GOALKEEPING_SHOT_STOPPING: 0x33,
    StaffMetric.MOTIVATING: 0x37,
    StaffMetric.TACTICAL_KNOWLEDGE: 0x39,
    StaffMetric.ATTACKING: 0x3A,
    StaffMetric.DEFENDING: 0x3B,
    StaffMetric.FITNESS: 0x3C,
    StaffMetric.MENTAL: 0x3D,
    StaffMetric.TECHNICAL: 0x3E,
    StaffMetric.TACTICAL: 0x3F,
    StaffMetric.GOALKEEPING_HANDLING: 0x41,
    StaffMetric.GOALKEEPING_DISTRIBUTION: 0x42,
    StaffMetric.SET_PIECES: 0x4B,
}


STAFF_AREA_WEIGHTS = {
    StaffArea.GOALKEEPING_SHOT_STOPPING: {2: StaffMetric.DDM, 9: StaffMetric.GOALKEEPING_SHOT_STOPPING},
    StaffArea.GOALKEEPING_HANDLING: {2: StaffMetric.DDM, 3: StaffMetric.GOALKEEPING_DISTRIBUTION, 6: StaffMetric.GOALKEEPING_HANDLING},
    StaffArea.DEFENDING_TACTICAL: {2: StaffMetric.DDM, 3: StaffMetric.TACTICAL, 6: StaffMetric.DEFENDING},
    StaffArea.DEFENDING_TECHNICAL: {2: StaffMetric.DDM, 3: StaffMetric.TECHNICAL, 6: StaffMetric.DEFENDING},
    StaffArea.ATTACKING_TACTICAL: {2: StaffMetric.DDM, 3: StaffMetric.TACTICAL, 6: StaffMetric.ATTACKING},
    StaffArea.ATTACKING_TECHNICAL: {2: StaffMetric.DDM, 3: StaffMetric.TECHNICAL, 6: StaffMetric.ATTACKING},
    StaffArea.POSSESSION_TACTICAL: {2: StaffMetric.DDM, 3: StaffMetric.MENTAL, 6: StaffMetric.TACTICAL},
    StaffArea.POSSESSION_TECHNICAL: {2: StaffMetric.DDM, 3: StaffMetric.MENTAL, 6: StaffMetric.TECHNICAL},
    StaffArea.FITNESS_STRENGTH: {2: StaffMetric.DDM, 9: StaffMetric.FITNESS},
    StaffArea.FITNESS_QUICKNESS: {2: StaffMetric.DDM, 9: StaffMetric.FITNESS},
    StaffArea.SET_PIECES: {2: StaffMetric.DDM, 3: StaffMetric.TACTICAL_KNOWLEDGE, 6: StaffMetric.SET_PIECES},
}

COACHING_AREAS = tuple(STAFF_AREA_WEIGHTS)
COACHING_AREA_COLUMNS = [area.value for area in COACHING_AREAS]


def decode_qualification(raw_value):
    studying = raw_value >= 100
    value = 0x101 - raw_value if studying else raw_value
    try:
        return Qualification(value), studying
    except ValueError:
        return None, studying
