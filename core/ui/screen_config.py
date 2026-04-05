"""Auto-generated screen calibration values."""

class StarsCalibration:
    def __init__(self, region, colour, half_increment, full_increment):
        self.region = region
        self.colour = colour
        self.half_increment = half_increment
        self.full_increment = full_increment


class RatingsCalibration:
    def __init__(self, region, pixels_per_rating, colours):
        self.region = region
        self.pixels_per_rating = pixels_per_rating
        self.colours = colours


class ContinueButtonCalibration:
    def __init__(self, xy, colour, tolerance):
        self.xy = xy
        self.colour = colour
        self.tolerance = tolerance


STARS = StarsCalibration(region=(1686, 359, 85, 24), colour=(244, 188, 0), half_increment=11, full_increment=25)

RATINGS = RatingsCalibration(
    region=(1389, 324, 63, 692),
    pixels_per_rating=175,
    colours={"A": (73, 230, 35), "B": (168, 222, 29), "C": (255, 214, 79), "D": (255, 135, 71), "E": (255, 108, 73), "F": (255, 84, 84)},
)

CONTINUE_BUTTON = ContinueButtonCalibration(xy=(1772, 31), colour=(112, 61, 191), tolerance=10)
RELOAD_DIALOG_NO_BUTTON = (1041, 580)
