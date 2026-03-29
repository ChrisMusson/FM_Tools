"""Auto-generated screen calibration values."""

from dataclasses import dataclass

Point = tuple[int, int]
Region = tuple[int, int, int, int]
Colour = tuple[int, int, int]


@dataclass(frozen=True)
class StarsCalibration:
    region: Region
    colour: Colour
    half_increment: int
    full_increment: int


@dataclass(frozen=True)
class RatingsCalibration:
    region: Region
    pixels_per_rating: int
    colours: dict[str, Colour]


@dataclass(frozen=True)
class ContinueButtonCalibration:
    xy: Point
    colour: Colour
    tolerance: int


STARS = StarsCalibration(
    region=(1686, 359, 85, 24),
    colour=(244, 188, 0),
    half_increment=11,
    full_increment=25,
)

RATINGS = RatingsCalibration(
    region=(1389, 324, 63, 692),
    pixels_per_rating=175,
    colours={
        "A": (73, 230, 35),
        "B": (168, 222, 29),
        "C": (255, 214, 79),
        "D": (255, 135, 71),
        "E": (255, 108, 73),
        "F": (255, 84, 84),
    },
)

CONTINUE_BUTTON = ContinueButtonCalibration(
    xy=(1772, 31),
    colour=(112, 61, 191),
    tolerance=10,
)

RELOAD_DIALOG_NO_BUTTON: Point = (1041, 580)
