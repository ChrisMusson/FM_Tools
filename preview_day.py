from time import sleep

from core.screen_probe import read_letter_ratings, read_star_rating
from core.ui_automation import InputController, advance_one_day, reload_last_save

START_DELAY_SECONDS = 3  # how long you have from running the script to make the FM24 window active
ACTION_PAUSE_SECONDS = 1  # how long to wait between actions (mouse clicks, key presses, etc.)

# stops when the letter rating of the intake preview is alphabetically at or before this grade string
STOP_AT_OR_BELOW_GRADE = "AAF"
# stops when the star rating of the intake preview reaches this value or higher
STOP_AT_OR_ABOVE_STARS = 4


def should_stop_preview_loop(grade_string: str, stars: float):
    return grade_string <= STOP_AT_OR_BELOW_GRADE or stars >= STOP_AT_OR_ABOVE_STARS


def main():
    controller = InputController(action_pause=ACTION_PAUSE_SECONDS)
    reload_last_save(controller)
    trial = 0

    while True:
        try:
            trial += 1
            advance_one_day(controller)
            controller.press("f4")

            stars, yellow_pixels = read_star_rating()
            if stars == 0:
                controller.press("f4")
                stars, yellow_pixels = read_star_rating()

            ratings = read_letter_ratings()
            print(f"Trial {trial}: {ratings} {stars:.1f} stars ({yellow_pixels} yellow pixels)")

            if stars == 0 or ratings == "":
                reload_last_save(controller)
                continue

            if should_stop_preview_loop(ratings, stars):
                return

            reload_last_save(controller)
        except Exception as exc:
            print(exc)
            reload_last_save(controller)


if __name__ == "__main__":
    sleep(START_DELAY_SECONDS)
    main()
