"""Find the best coach allocation by total coaching role score."""

from core.memory.process import open_fm_process
from core.scouting.staff.optimiser import (
    build_assignment_table,
    get_active_coaching_areas,
    load_coach_candidates,
    solve_best_coach_assignments,
    validate_uid_constraints,
)
from core.scouting.staff.roles import COACHING_AREA_COLUMNS, TRAINING_AREAS
from core.scouting.staff.shortlist import DEFAULT_STAFF_SHORTLIST_PATH

# Configuration
SHORTLIST_PATH = DEFAULT_STAFF_SHORTLIST_PATH  # default shortlist path is "staff_shortlist.html"
ALLOWED_CLUBS = []  # leave as empty if you are happy using anyone in the shortlist
EXCLUDED_AREAS = [TRAINING_AREAS.SET_PIECES]  # training areas to ignore entirely
INCLUDE_CURRENT_CLUB_STAFF = True  # add the current manager's club staff from memory even if they are not in the shortlist export
MIN_ANY_CATEGORY_STARS = 4  # set to e.g. 4 or 4.5 to keep only coaches with at least one category at this star rating
EXTRA_UIDS = []  # UIDs to load directly from memory even if they do not appear in the shortlist (e.g. new coach signings)
INCLUDED_UIDS = []  # UIDs of people who must be in the solution
EXCLUDED_UIDS = []  # UIDs of people who must not be in the solution


def main():
    process = open_fm_process()
    validate_uid_constraints(INCLUDED_UIDS, EXCLUDED_UIDS)
    area_columns = get_active_coaching_areas(EXCLUDED_AREAS)
    filtered_df, metadata = load_coach_candidates(
        SHORTLIST_PATH,
        process,
        allowed_clubs=ALLOWED_CLUBS,
        included_uids=INCLUDED_UIDS,
        excluded_uids=EXCLUDED_UIDS,
        extra_uids=EXTRA_UIDS,
        include_current_club_staff=INCLUDE_CURRENT_CLUB_STAFF,
    )
    if MIN_ANY_CATEGORY_STARS:
        qualifying_mask = filtered_df[COACHING_AREA_COLUMNS].fillna(0).ge(MIN_ANY_CATEGORY_STARS).any(axis=1)
        filtered_df = filtered_df.loc[qualifying_mask].reset_index(drop=True)
    if filtered_df.empty:
        raise ValueError("No staff remained after applying the configured filters")

    result = solve_best_coach_assignments(filtered_df, area_columns, included_uids=INCLUDED_UIDS)
    assignments_df = build_assignment_table(filtered_df, result, area_columns).set_index("Area")

    print(f"Loaded {metadata['shortlist_count']:,} shortlisted staff.")
    if metadata["manager_status"] == "added":
        print("Added current manager as an extra coach candidate.")
    elif metadata["manager_status"] == "marked":
        print("Marked the current manager in the candidate pool.")
    else:
        print("Could not load the current manager as a coach candidate.")
        print(f"Reason: {metadata['manager_error']}")
    print(f"Filtered pool: {len(filtered_df):,} coach(es).")
    if ALLOWED_CLUBS:
        allowed_club_labels = ["None" if club is None else str(club) for club in ALLOWED_CLUBS]
        print(f"Allowed clubs: {', '.join(allowed_club_labels)}")
    if EXCLUDED_AREAS:
        print(f"Excluded areas: {', '.join(area.value for area in EXCLUDED_AREAS)}")
    if INCLUDE_CURRENT_CLUB_STAFF and metadata["current_club_staff_uids"]:
        print(f"Added current club staff: {', '.join(str(uid) for uid in metadata['current_club_staff_uids'])}")
    if MIN_ANY_CATEGORY_STARS:
        print(f"Minimum stars in any category: {MIN_ANY_CATEGORY_STARS}")
    if EXTRA_UIDS:
        print(f"Extra UIDs: {', '.join(str(uid) for uid in EXTRA_UIDS)}")
    if metadata["missing_extra_uids"]:
        print(f"Extra UIDs not found in memory: {', '.join(str(uid) for uid in metadata['missing_extra_uids'])}")
    if INCLUDED_UIDS:
        print(f"Included UIDs: {', '.join(str(uid) for uid in INCLUDED_UIDS)}")
    if EXCLUDED_UIDS:
        print(f"Excluded UIDs: {', '.join(str(uid) for uid in EXCLUDED_UIDS)}")
    print()
    print(f"Best unique-coach allocation across {len(area_columns):,} areas: {result['total_role_score']:,} total coaching role score.")
    print()
    print(assignments_df)


if __name__ == "__main__":
    main()
