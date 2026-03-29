# FM_Intake_Reloader

FM_Intake_Reloader is a small automation project for Football Manager youth intake reloading.

It does two main jobs:

- `preview_day.py` reloads the preview day until the quality of the intake preview meets the threshold you choose.
- `intake_day.py` reloads the actual intake day and checks the generated players' `CA` and `PA` directly from game memory, stopping when the CA and PA meet the threshold you choose.

The project is designed so the main scripts you run are at the root of the repo. Everything inside `core/` is internal support code, while everything inside `tools/` is for calibration and/or debugging.

## What It Does

On the preview day, the script `preview_day.py`:

- reloads
- advances once to the youth intake preview
- reads the star rating from the screen
- reads the letter grades from the screen
- repeats this until the preview meets your chosen thresholds

On intake day, the script `intake_day.py`:

- reloads
- advances once to the youth intake
- checks the `CA` and `PA` of players in the youth intake
- repeats reloading until the intake meets your chosen thresholds

## Scripts

Before you can do this though, you need to calibrate the script to work on your screen size / zoom / skin. To do this, you need to run `tools/calibration.py` and follow all the instructions on there. This is best done on a youth intake preview day, so that you can accurately measure where the star rating region is. However, you can just skip through that if you are not near the youth intake preview day.

## Platform Support

The repo is intended to work on both Windows and Linux.

- Screen reading and input automation use different backends depending on the OS.
- Squad data reading uses OS-specific process-memory access behind one shared interface.

The scripts are meant to be run from the project root, or from `tools/` for the helper scripts. You should not need to run anything inside `core/` directly.

## Typical Workflow

1. Run `tools/calibration.py` once to set up your screen positions
2. Open Football Manager and get to the relevant screen
3. Open `preview_day.py` or `intake_day.py`
4. Edit the stop condition for your chosen script
5. Run the script 
6. Let the script keep reloading until it finds a result worth keeping

## Notes

- The scripts assume Football Manager is visible, focused, and in the same layout you calibrated for.
- On Linux, install `spectacle`. This repo uses it for screenshots and it is the backend we know works reliably.
  - Debian-based: `sudo apt install kde-spectacle`.
  - Fedora: `sudo dnf install spectacle`.
  - Arch: `sudo pacman -S spectacle`.
  - On other distros, look for a package called `spectacle` or `kde-spectacle`.
- On Windows, the game and script should be running with compatible permissions so input and memory reading both work properly.
