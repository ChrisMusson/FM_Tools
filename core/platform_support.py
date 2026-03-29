"""Platform helpers shared by the scripts in this repo."""

import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
IS_WINDOWS = sys.platform.startswith("win")
IS_LINUX = sys.platform.startswith("linux")


def require_supported_platform():
    if not (IS_WINDOWS or IS_LINUX):
        raise RuntimeError(f"Unsupported platform: {sys.platform}")


def enable_windows_dpi_awareness():
    """Keep Tk, screenshots, and clicks on the same coordinate system."""
    if not IS_WINDOWS:
        return

    try:
        import ctypes

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


require_supported_platform()
enable_windows_dpi_awareness()
