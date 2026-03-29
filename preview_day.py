from time import sleep

from core.screen_probe import read_letter_ratings, read_star_rating
from core.ui_automation import create_input_controller, reload_last_save, wait_for_continue_button

START_DELAY_SECONDS = 3  # how long you have from running the script to make the FM24 window active
ACTION_PAUSE_SECONDS = 1  # how long to wait between actions (mouse clicks, key presses, etc.)

STOP_AT_OR_BELOW_GRADE = "AFF"  # stops when the letter rating of the intake is better than AFF (sorted lexicographically)
STOP_AT_OR_ABOVE_STARS = 2  # stops when star rating of the intake preview is 2 stars or above


def grade_sort_key(grade_string: str):
    return [ord(character) for character in grade_string]


def should_stop_preview_loop(grade_string: str, stars: float):
    return grade_sort_key(grade_string) <= grade_sort_key(STOP_AT_OR_BELOW_GRADE) or stars >= STOP_AT_OR_ABOVE_STARS


"""Reload the preview day until the intake preview looks good enough to keep."""


def main():
    controller = create_input_controller(action_pause=ACTION_PAUSE_SECONDS)
    reload_last_save(controller)
    trial = 0

    while True:
        try:
            trial += 1
            sleep(1)
            controller.press("space")
            controller.press("escape")
            wait_for_continue_button()
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
