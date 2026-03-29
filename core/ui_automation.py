"""Cross-platform mouse and keyboard helpers for the FM UI."""

from time import monotonic, sleep

from core.platform_support import IS_LINUX, IS_WINDOWS
from core.screen_config import CONTINUE_BUTTON, RELOAD_DIALOG_NO_BUTTON
from core.screen_probe import sample_pixel

WAIT_TIMEOUT_SECONDS = 180
POLL_INTERVAL_SECONDS = 1

WINDOWS_KEY_NAMES = {
    "slash": "/",
    "space": "space",
    "escape": "esc",
    "f4": "f4",
}

WINDOWS_BUTTON_NAMES = {
    1: "left",
    2: "middle",
    3: "right",
}

LINUX_KEY_NAMES = {
    "slash": "slash",
    "space": "space",
    "escape": "Escape",
    "f4": "F4",
}


class InputController:
    def __init__(self, action_pause: float = 1):
        self.action_pause = action_pause
        if IS_WINDOWS:
            import pyautogui

            self.platform = "windows"
            self.pyautogui = pyautogui
        elif IS_LINUX:
            from Xlib import XK, X, display
            from Xlib.ext import xtest

            self.platform = "linux"
            self.XK = XK
            self.X = X
            self.xtest = xtest
            self.display = display.Display()
            self.root = self.display.screen().root
        else:
            raise RuntimeError("Unsupported platform")

    def press(self, key_name: str):
        if self.platform == "windows":
            self.pyautogui.press(WINDOWS_KEY_NAMES[key_name])
        else:
            keysym = self.XK.string_to_keysym(LINUX_KEY_NAMES[key_name])
            keycode = self.display.keysym_to_keycode(keysym)
            if keycode == 0:
                raise ValueError(f"Unknown key name: {key_name}")
            self.xtest.fake_input(self.display, self.X.KeyPress, keycode)
            self.xtest.fake_input(self.display, self.X.KeyRelease, keycode)
            self.display.sync()
        sleep(self.action_pause)

    def click(self, x: int, y: int, button: int = 1):
        if self.platform == "windows":
            self.pyautogui.click(x=x, y=y, button=WINDOWS_BUTTON_NAMES.get(button, "left"))
        else:
            self.root.warp_pointer(x, y)
            self.display.sync()
            sleep(0.05)
            self.xtest.fake_input(self.display, self.X.ButtonPress, button)
            self.xtest.fake_input(self.display, self.X.ButtonRelease, button)
            self.display.sync()
        sleep(self.action_pause)


def create_input_controller(action_pause: float = 1):
    return InputController(action_pause=action_pause)


def _pixel_matches(pixel, target_colour, tolerance: int = 0):
    return all(abs(int(pixel[index]) - int(target_colour[index])) <= tolerance for index in range(3))


def wait_for_continue_button(
    timeout: float = WAIT_TIMEOUT_SECONDS,
    poll_interval: float = POLL_INTERVAL_SECONDS,
):
    deadline = monotonic() + timeout
    last_seen = None

    while monotonic() < deadline:
        last_seen = sample_pixel(CONTINUE_BUTTON.xy)
        if _pixel_matches(last_seen, CONTINUE_BUTTON.colour, CONTINUE_BUTTON.tolerance):
            return
        sleep(poll_interval)

    raise TimeoutError(
        "Timed out waiting for the Continue button pixel "
        f"{CONTINUE_BUTTON.xy} to match {CONTINUE_BUTTON.colour} within tolerance {CONTINUE_BUTTON.tolerance}; "
        f"last seen {last_seen}"
    )


def reload_last_save(controller: InputController):
    controller.press("slash")
    controller.click(*RELOAD_DIALOG_NO_BUTTON)
    wait_for_continue_button()
