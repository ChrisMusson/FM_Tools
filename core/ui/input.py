"""Cross-platform mouse and keyboard helpers for the FM UI."""

from time import monotonic, sleep

from core.platform import IS_WINDOWS
from core.ui.screen import sample_pixel
from core.ui.screen_config import CONTINUE_BUTTON, RELOAD_DIALOG_NO_BUTTON

WAIT_TIMEOUT_SECONDS = 180
POLL_INTERVAL_SECONDS = 1
RELOAD_SHORTCUT = ("ctrl", "shift", "r")  # Football Manager default: Load Last Save


def _windows_key_name(key_name):
    return {"escape": "esc"}.get(key_name, key_name)


def _windows_button_name(button):
    return {1: "left", 2: "middle", 3: "right"}.get(button, "left")


def _linux_key_name(key_name):
    return {"ctrl": "Control_L", "shift": "Shift_L", "escape": "Escape", "f4": "F4"}.get(key_name, key_name)


class InputController:
    def __init__(self, action_pause=1):
        self.action_pause = action_pause
        if IS_WINDOWS:
            import pyautogui

            self.platform = "windows"
            self.pyautogui = pyautogui
        else:
            from Xlib import XK, X, display
            from Xlib.ext import xtest

            self.platform = "linux"
            self.XK = XK
            self.X = X
            self.xtest = xtest
            self.display = display.Display()
            self.root = self.display.screen().root

    def press(self, key_name):
        if self.platform == "windows":
            self.pyautogui.press(_windows_key_name(key_name))
        else:
            keycode = self._linux_keycode(key_name)
            self.xtest.fake_input(self.display, self.X.KeyPress, keycode)
            self.xtest.fake_input(self.display, self.X.KeyRelease, keycode)
            self.display.sync()
        sleep(self.action_pause)

    def hotkey(self, *key_names):
        if self.platform == "windows":
            self.pyautogui.hotkey(*(_windows_key_name(key_name) for key_name in key_names))
        else:
            keycodes = [self._linux_keycode(key_name) for key_name in key_names]
            for keycode in keycodes:
                self.xtest.fake_input(self.display, self.X.KeyPress, keycode)
            for keycode in reversed(keycodes):
                self.xtest.fake_input(self.display, self.X.KeyRelease, keycode)
            self.display.sync()
        sleep(self.action_pause)

    def click(self, x, y, button=1):
        if self.platform == "windows":
            self.pyautogui.click(x=x, y=y, button=_windows_button_name(button))
        else:
            self.root.warp_pointer(x, y)
            self.display.sync()
            sleep(0.05)
            self.xtest.fake_input(self.display, self.X.ButtonPress, button)
            self.xtest.fake_input(self.display, self.X.ButtonRelease, button)
            self.display.sync()
        sleep(self.action_pause)

    def _linux_keycode(self, key_name):
        keysym = self.XK.string_to_keysym(_linux_key_name(key_name))
        keycode = self.display.keysym_to_keycode(keysym)
        if keycode == 0:
            raise ValueError(f"Unknown key name: {key_name}")
        return keycode


def _pixel_matches(pixel, target_colour, tolerance=0):
    return all(abs(int(pixel[index]) - int(target_colour[index])) <= tolerance for index in range(3))


def wait_for_continue_button(timeout=WAIT_TIMEOUT_SECONDS, poll_interval=POLL_INTERVAL_SECONDS):
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


def advance_one_day(controller, settle_seconds=1):
    sleep(settle_seconds)
    controller.press("space")
    controller.press("escape")
    wait_for_continue_button()


def reload_last_save(controller):
    controller.hotkey(*RELOAD_SHORTCUT)
    controller.click(*RELOAD_DIALOG_NO_BUTTON)
    wait_for_continue_button()
