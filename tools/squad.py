"""Print squad CA and PA data for one or more team buckets."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.squad_data import load_squad_table

DEFAULT_TEAM_IDS = [0, 1]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target-team",
        dest="target_teams",
        action="append",
        type=int,
        help="Team bucket id to include. Repeat the flag to include more than one.",
    )
    parser.add_argument("--limit", type=int, default=20, help="How many rows to print")
    return parser.parse_args()


def main():
    args = parse_args()
    target_teams = args.target_teams or DEFAULT_TEAM_IDS
    squad = load_squad_table(target_teams=target_teams)
    print(squad.head(args.limit).to_string(index=False))


if __name__ == "__main__":
    main()
