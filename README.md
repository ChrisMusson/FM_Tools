# FM_Intake_Reloader

FM_Intake_Reloader is a small cross-platform Football Manager toolkit.

It currently supports two main workflows:

- `preview_day.py` and `intake_day.py` automate youth intake reloading.
- `player_scan.py` reads player data from game memory and builds an HTML report for the roles you care about.

The project is designed so the main scripts you run are at the root of the repo. Everything inside `core/` is internal support code, while everything inside `tools/` is for calibration and/or debugging.

## What It Does

For youth intakes, `preview_day.py`:

- reloads
- advances once to the youth intake preview
- reads the star rating from the screen
- reads the letter grades from the screen
- repeats this until the preview meets your chosen thresholds

For youth intakes, `intake_day.py`:

- reloads
- advances once to the youth intake
- checks the `CA` and `PA` of players in the youth intake
- repeats reloading until the intake meets your chosen thresholds

For player scouting, `player_scan.py`:

- reads a saved `shortlist.html` export from Football Manager
- matches those players to live memory data
- scores them for the roles you choose
- writes the results to `table.html`

## Scripts

Before using the preview/intake scripts, you need to calibrate the screen-reading positions for your layout, zoom, and skin. To do this, run `uv run -m tools.calibration` and follow the instructions. This is best done on a youth intake preview day, so that you can accurately measure where the star rating region is.

The helper scripts in `tools/` are intended to be run as modules:

- `uv run -m tools.calibration`
- `uv run -m tools.squad`

## Platform Support

The repo is intended to work on both Windows and Linux.

- Screen reading and input automation use different backends depending on the OS.
- Squad data reading uses OS-specific process-memory access behind one shared interface.

The scripts are meant to be run from the project root. You should not need to run anything inside `core/` or `tools/` directly.

## Typical Workflows

### Preview / Intake Reloading

1. Make a save just before the youth intake preview day or the youth intake day.
2. Run `uv run -m tools.calibration` once to set up your screen positions.
3. Open Football Manager and load that save.
4. Open either `preview_day.py` or `intake_day.py`.
5. Edit the stop condition for the script you want to use.
6. Run the script, for example `uv run preview_day.py`.
7. Let it keep reloading until it finds a result that meets your threshold.

### Player Scan

1. Open Football Manager whenever you want to scan players.
2. Go to the player search screen and apply whatever filters you want.
3. Make sure your player search view includes `UID`. Everything else is optional, though columns like `Age`, `Position`, `Club`, `Nationality`, and `Wage` make the output more useful.
4. Press `Ctrl+A` to select all players.
5. Press `Ctrl+P`, choose `Web Page`, and save the file as `shortlist.html` in the root of this repo.
6. Open `player_scan.py` and change the `ROLES` list to the roles you want to score.
7. Run `uv run player_scan.py`.
8. Open `table.html` to view the results.

## Notes

- The scripts assume Football Manager is visible, focused, and in the same layout you calibrated for.
- On Linux, install `spectacle`. This repo uses it for screenshots and it is the backend we know works reliably.
  - Debian-based: `sudo apt install kde-spectacle`.
  - Fedora: `sudo dnf install spectacle`.
  - Arch: `sudo pacman -S spectacle`.
  - On other distros, look for a package called `spectacle` or `kde-spectacle`.
- On Windows, the game and script should be running with compatible permissions so input and memory reading both work properly.
